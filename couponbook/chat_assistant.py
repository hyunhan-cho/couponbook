"""
쿠폰북 AI 어시스턴트
사용자의 질문에 대화형으로 답변하고, 쿠폰 사용법/가게 정보/추천 등을 제공합니다.
"""

from decouple import config
from openai import OpenAI
from accounts.models import User
from couponbook.models import Coupon, CouponTemplate, Place
from django.utils.timezone import now
from django.db.models import Q, Count
import json


class CouponbookAssistant:
    """
    사용자의 쿠폰북 정보를 기반으로 대화형 AI 어시스턴트 기능을 제공합니다.
    """

    def __init__(self, user: User, openai_api_key: str = ""):
        """
        사용자와 OpenAI API 키를 받아 어시스턴트를 초기화합니다.
        """
        self.user = user
        self.api_key = openai_api_key or config("OPENAI_API_KEY", default="")
        self.client: OpenAI | None = None
        
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)

    def _get_user_context(self) -> dict:
        """
        사용자의 쿠폰북 정보를 수집하여 AI에게 제공할 컨텍스트를 생성합니다.
        """
        try:
            # 사용자의 쿠폰 목록
            coupons = Coupon.objects.filter(
                couponbook__user=self.user
            ).select_related('original_template__place').annotate(
                stamp_count=Count('stamps')
            )

            user_coupons = []
            for coupon in coupons:
                template = coupon.original_template
                place = template.place
                user_coupons.append({
                    "가게명": place.name,
                    "주소": f"{place.address_district.province} {place.address_district.city} {place.address_district.district}",
                    "쿠폰명": template.name,
                    "현재_스탬프": coupon.stamp_count,
                    "필요_스탬프": template.reward_info.amount,
                    "리워드": template.reward,
                    "태그": place.tags if hasattr(place, 'tags') else []
                })

            # 사용자 선호 지역
            favorite_locations = []
            if hasattr(self.user, 'favorite_locations'):
                for loc in self.user.favorite_locations.all():
                    favorite_locations.append({
                        "광역시도": loc.province,
                        "시군구": loc.city,
                        "법정동": loc.district
                    })

            # 주변 이용 가능한 쿠폰 템플릿 (최대 10개)
            available_templates = CouponTemplate.objects.filter(
                Q(valid_until=None) | Q(valid_until__gte=now()),
                is_on=True
            ).exclude(
                coupons__couponbook__user=self.user
            ).select_related('place__address_district')[:10]

            nearby_templates = []
            for template in available_templates:
                place = template.place
                nearby_templates.append({
                    "가게명": place.name,
                    "주소": f"{place.address_district.province} {place.address_district.city} {place.address_district.district}",
                    "쿠폰명": template.name,
                    "필요_스탬프": template.reward_info.amount,
                    "리워드": template.reward,
                    "태그": place.tags if hasattr(place, 'tags') else []
                })

            return {
                "사용자명": self.user.username,
                "보유_쿠폰": user_coupons,
                "선호_지역": favorite_locations,
                "주변_이용가능_쿠폰": nearby_templates[:5]  # 5개만 제공
            }

        except Exception as e:
            print(f"컨텍스트 생성 오류: {e}")
            return {
                "사용자명": self.user.username,
                "보유_쿠폰": [],
                "선호_지역": [],
                "주변_이용가능_쿠폰": []
            }

    def chat(self, user_message: str, conversation_history: list = None) -> dict:
        """
        사용자 메시지를 받아 AI 어시스턴트의 응답을 생성합니다.
        
        Args:
            user_message: 사용자의 질문/메시지
            conversation_history: 이전 대화 기록 (선택)
            
        Returns:
            {
                "response": "AI 응답 메시지",
                "context_used": True/False  # 사용자 데이터를 사용했는지 여부
            }
        """
        
        # OpenAI 클라이언트가 없으면 fallback 메시지
        if not self.client:
            return {
                "response": "죄송합니다. AI 어시스턴트 기능이 현재 사용 불가능합니다. 관리자에게 문의해주세요.",
                "context_used": False,
                "error": "OPENAI_API_KEY not configured"
            }

        try:
            # 사용자 컨텍스트 수집
            user_context = self._get_user_context()
            context_json = json.dumps(user_context, ensure_ascii=False, indent=2)

            # 시스템 프롬프트
            system_prompt = """
당신은 '쿠폰북' 앱의 친절한 AI 어시스턴트입니다.

**역할:**
1. 사용자의 쿠폰 사용을 돕습니다
2. 보유한 쿠폰 정보를 알려줍니다
3. 주변 가게와 이용 가능한 쿠폰을 추천합니다
4. 앱 사용법을 안내합니다
5. 친근하고 자연스럽게 대화합니다

**답변 규칙:**
- 반말로 친근하게 대화하세요
- 이모지를 적절히 사용하세요
- 간결하고 명확하게 답변하세요
- 사용자 데이터를 기반으로 개인화된 답변을 제공하세요
- 정보가 없으면 솔직하게 "모르겠어", "정보가 없어" 라고 답하세요

**쿠폰북 앱 기능:**
- 가게 쿠폰 저장하기
- 방문 시 영수증 번호로 스탬프 적립
- 스탬프 다 모으면 리워드 받기
- 즐겨찾기로 자주 가는 가게 관리
- AI 추천으로 새로운 가게 발견
"""

            # 메시지 구성
            messages = [
                {"role": "system", "content": system_prompt}
            ]

            # 대화 히스토리 추가 (있으면)
            if conversation_history:
                messages.extend(conversation_history)

            # 사용자 컨텍스트와 질문 추가
            user_content = f"""
[사용자 정보]
{context_json}

[사용자 질문]
{user_message}

위 정보를 참고하여 사용자의 질문에 답변해주세요.
"""
            messages.append({"role": "user", "content": user_content})

            # OpenAI API 호출
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            ai_response = response.choices[0].message.content

            return {
                "response": ai_response,
                "context_used": True,
                "user_context": user_context  # 디버깅용 (프로덕션에서는 제거 가능)
            }

        except Exception as e:
            # 오류 발생 시 안전한 fallback
            return {
                "response": f"죄송해요, 일시적인 오류가 발생했어요. 다시 한번 물어봐 주실래요? 🙏",
                "context_used": False,
                "error": str(e)
            }

    def get_quick_suggestions(self) -> list[str]:
        """
        사용자가 물어볼 만한 질문 예시를 생성합니다.
        """
        suggestions = [
            "내 쿠폰 몇 개야?",
            "스탬프 많이 모은 쿠폰 알려줘",
            "근처 카페 추천해줘",
            "이 쿠폰 어떻게 사용해?",
            "즐겨찾기는 뭐야?",
        ]
        
        try:
            coupon_count = Coupon.objects.filter(couponbook__user=self.user).count()
            if coupon_count > 0:
                suggestions.insert(0, "내가 가진 쿠폰 보여줘")
            
            if hasattr(self.user, 'favorite_locations') and self.user.favorite_locations.exists():
                loc = self.user.favorite_locations.first()
                suggestions.append(f"{loc.district}에 뭐 있어?")
        except:
            pass
            
        return suggestions

