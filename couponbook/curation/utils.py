from datetime import datetime
from json import dumps, loads

from accounts.models import User
from couponbook.models import *
from decouple import config
from openai import OpenAI

from .serializers import CouponTemplateDictSerializer


class UserStatistics:
    """
    유저의 쿠폰북 이용 통계 클래스입니다. AI의 큐레이션 기능에 활용됩니다.
    """
    def __init__(self, user: User, time_format="%Y-%m-%d %H:%M"):
        """
        유저 인스턴스와 시간 포맷팅 문자열을 인자로 받습니다. 유저 인스턴스는 필수이며, 시간 포맷팅 문자열은 전달하지 않으면 기본값으로 설정됩니다.
        
        시간 포맷팅 기본값: `%Y-%m-%d %H:%M` (4자리 연도-월-일 시:분)
        """

        self.user: User = user
        self.time_format: str = time_format

    @property
    def own_couponbook(self):
        """
        해당 유저의 쿠폰북을 가져옵니다.
        """

        try:
            couponbook = CouponBook.objects.get(user=self.user)
            return couponbook
        except CouponBook.DoesNotExist:
            print("유저의 쿠폰북이 존재하지 않습니다.")

    def format_time(self, time: datetime) -> str:
        """
        datetime 인스턴스를 받아 해당 인스턴스의 시간 정보를 통계 객체의 시간 포맷팅에 맞게 포맷팅한 문자열로 반환합니다.
        """

        time_format = self.time_format
        return time.strftime(time_format)

    def extract_legal_district(self, legal_district: LegalDistrict):
        """
        가게의 법정동 주소 인스턴스를 받아서, 광역시 ~ 법정동 주소를 연결한 문자열을 반환합니다.
        """

        return f"{legal_district.province} {legal_district.city} {legal_district.district}"
    
    def extract_address(self, place: Place):
        """
        가게 인스턴스를 받아서, 가게의 주소를 문자열로 반환합니다.
        """

        return f"{self.extract_legal_district(place.address_district)} {place.address_rest}"
    
    def extract_place_info(self, place: Place) -> dict[str, str]:
        """
        가게 인스턴스를 받아서, 가게의 정보를 딕셔너리 안에 넣어서 반환합니다.
        """

        place_info = {}
        place_info['name'] = place.name
        place_info['address'] = self.extract_address(place)
        place_info['tags'] = place.tags
        return place_info
    
    def calc_current_stamps(self, coupon: Coupon) -> int:
        """
        현재까지 적립된 스탬프 수를 계산합니다.
        """

        stamps = coupon.stamps
        return stamps.count()
    
    def calc_max_stamps(self, coupon_template: CouponTemplate) -> int:
        """
        쿠폰 완성을 위해 스탬프가 몇개 필요한지를 계산합니다.
        """

        reward_info: RewardsInfo = coupon_template.reward_info
        return reward_info.amount
    
    def make_stamp_history(self, coupon: Coupon) -> list[dict]:
        """
        해당 쿠폰의 스탬프 적립 히스토리를 만듭니다.
        """

        stamps = coupon.stamps.order_by('created_at')
        history_list = []
        for number, stamp in enumerate(stamps, start=1):
            stamp_data = {}
            stamp_data['count'] = number
            stamp_data['created_at'] = self.format_time(stamp.created_at)
            history_list.append(stamp_data)
        return history_list
    
    def make_coupon_data(self, coupon: Coupon) -> dict:
        """
        쿠폰의 데이터를 만들어 딕셔너리로 반환합니다.
        """

        data = {}
        original_template = coupon.original_template
        data['place_info'] = self.extract_place_info(original_template.place)
        data['max_stamps'] = self.calc_max_stamps(original_template)
        data['current_stamps'] = self.calc_current_stamps(coupon)
        data['stamp_history'] = self.make_stamp_history(coupon)
        return data
    
    def make_history(self) -> list[dict]:
        """
        현재 보유하고 있는 쿠폰과, 쿠폰에 연결된 가게, 스탬프 적립 기록을 만들어 반환합니다.
        """

        coupons = Coupon.objects.filter(couponbook=self.own_couponbook)
        history = []
        for coupon in coupons:
            coupon_dict = {}
            coupon_dict['id'] = coupon.id
            coupon_dict['data'] = self.make_coupon_data(coupon)
            history.append(coupon_dict)
        return history

class AICurator:
    """
    OpenAI를 이용하여 쿠폰 큐레이션 기능을 제공하는 큐레이터 객체입니다.
    """

    def __init__(self, openai_api_key: str = ""):
        """
        OpenAI API 키를 인자로 받습니다. 입력하지 않거나, 빈 문자열이면 .env의 OPENAI_API_KEY 값을 사용합니다.
        """

        # OPENAI_API_KEY를 .env에서 읽습니다. (없는 경우 빈 문자열)
        self.api_key = openai_api_key or config("OPENAI_API_KEY", default="")
        self.client: OpenAI | None = None
        if self.api_key:
            # 키가 없는 경우에도 서버가 죽지 않도록, 없는 경우에는 client를 생성하지 않습니다.
            self.client = OpenAI(api_key=self.api_key)

    def _build_prompt(self, statistics: UserStatistics, coupon_templates) -> str:
        """
        유저 통계와 쿠폰 템플릿 정보를 JSON 형태의 문자열로 만들어 프롬프트에 사용합니다.
        """

        statistics_history = statistics.make_history()
        input_data_dict = {
            "user_statistics": statistics_history,
            "coupon_templates": CouponTemplateDictSerializer(coupon_templates, many=True).data,
        }
        return dumps(input_data_dict, ensure_ascii=False)

    def curate(self, statistics: UserStatistics, coupon_templates) -> list[int]:
        """
        쿠폰 큐레이션을 실행합니다. 큐레이션 결과로 추천하는 쿠폰의 id 리스트가 반환됩니다.
        """

        # OpenAI 클라이언트가 없으면(키가 없거나 설정 안 됨) 단순 fallback: 상위 3개 추천
        if not self.client:
            return list(coupon_templates.values_list("id", flat=True)[:3])

        prompt_json = self._build_prompt(statistics, coupon_templates)

        system_message = (
            "너는 개인의 취향을 분석하고, 이를 토대로 주변의 음식점을 추천해주는 비서야. "
            "응답은 반드시 JSON 형식으로만 반환해. 형식: "
            '{"coupon_template_ids":[정수,...]}'
        )
        user_message = (
            "다음은 유저의 쿠폰 이용 내역과 현재 게시중인 쿠폰 템플릿 목록이야.\n"
            "이 정보를 보고 추천할 coupon_template의 id 3개를 배열 형태로 골라줘. "
            "만약 coupon_template이 3개 이하라면 모든 coupon_template의 id를 그대로 반환해.\n"
            "입력(JSON):\n"
            f"{prompt_json}\n\n"
            '출력은 예시처럼 JSON으로만: {"coupon_template_ids":[1,2,3]}'
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.2,
            )
            content = response.choices[0].message.content
            # content가 문자열이라고 가정하고 JSON 파싱
            data = loads(content)
            ids = data.get("coupon_template_ids", [])
            # 정수 리스트만 반환하도록 방어 코드
            return [int(i) for i in ids][:3]
        except Exception:
            # OpenAI 호출 실패 시에도 서버가 500으로 터지지 않도록 안전한 fallback
            return list(coupon_templates.values_list("id", flat=True)[:3])
