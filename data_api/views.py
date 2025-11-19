from pathlib import Path
from typing import List, Dict, Any

from django.conf import settings

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, serializers
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
import json
from functools import lru_cache

"""
위치(시/도-시/군/구-읍/면/동) 데이터를 반환하는 API 뷰
- GET /api/locations/ -> 전체 트리(JSON 파일 그대로)
- GET /api/locations/?province=서울특별시 -> 해당 시/도에 속한 시/군/구 목록(문자열 배열)
- GET /api/locations/?province=서울특별시&city=종로구 -> 해당 시/군/구의 읍/면/동 목록(문자열 배열)
"""

# locations.json 경로 (create_locations.py가 저장하는 위치와 동일)
LOC_FILE = Path(settings.BASE_DIR) / "modelproject" / "data" / "locations.json"

# 파일이 없을 때 최소한으로라도 내려줄 기본 위치 데이터
DEFAULT_LOCATIONS = {
    "서울특별시": {
        "종로구": ["청운동", "사직동", "평창동"],
        "중구": ["소공동", "회현동", "명동"],
    },
    "경기도": {
        "성남시": ["분당구", "수정구", "중원구"],
        "수원시": ["장안구", "권선구", "팔달구", "영통구"],
    },
}


@lru_cache(maxsize=1)
def _load_locations() -> dict:
    """
    파일을 읽어 딕셔너리로 반환합니다. (간단 캐시)
    파일이 갱신되면 서버 재시작 시 자동 반영됩니다.
    """
    try:
        with LOC_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
            # 비어 있는 dict면 의미 있는 데이터가 아니라고 보고 기본값 사용
            if data:
                return data
    except (FileNotFoundError, json.JSONDecodeError):
        # 아래에서 기본 데이터를 생성하도록 진행
        pass

    # 여기까지 왔다는 것은 파일이 없거나 손상된 상태이므로
    # 기본 데이터를 파일로 생성한 뒤 반환한다.
    LOC_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOC_FILE.open("w", encoding="utf-8") as f:
        json.dump(DEFAULT_LOCATIONS, f, ensure_ascii=False, indent=2)
    return DEFAULT_LOCATIONS


@extend_schema(
    tags=["Locations"],
    summary="법정동 위치 데이터 조회",
    description=
        """
        - GET /api/locations/ → 전체 트리(JSON)
        - GET /api/locations/?province=서울특별시 → 해당 시/도의 시/군/구 목록(문자열 배열)
        - GET /api/locations/?province=서울특별시&city=종로구 → 해당 시/군/구의 읍/면/동 목록(문자열 배열)
        """,
    parameters=[
        OpenApiParameter(
            name="province",
            type=str,
            required=False,
            description="시/도 이름 (예: 서울특별시, 경기도)",
        ),
        OpenApiParameter(
            name="city",
            type=str,
            required=False,
            description="시/군/구 이름 (예: 종로구, 성남시)",
        ),
    ],
    responses={200: OpenApiTypes.ANY},  # 전체 트리(Object) 또는 문자열 배열(Array) 반환
)
class LocationListAPIView(APIView):
    """
    위치 데이터 조회용 엔드포인트
    - 전체 구조: { 시도: { 시군구: [읍/면/동, ...] } }
    - 쿼리 파라미터로 부분 조회 지원
    """

    permission_classes = [AllowAny]

    def get(self, request):
        data = _load_locations()
        province = request.query_params.get("province")
        city = request.query_params.get("city")

        # 1) province & city → 해당 시/군/구의 읍/면/동 배열
        if province and city:
            districts = data.get(province, {}).get(city, [])
            return Response(districts, status=status.HTTP_200_OK)

        # 2) province만 → 해당 시/도의 시/군/구 목록
        if province:
            cities = list(data.get(province, {}).keys())
            return Response(cities, status=status.HTTP_200_OK)

        # 3) 파라미터 없음 → 전체 트리 반환
        return Response(data, status=status.HTTP_200_OK)


from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.core.files.storage import default_storage

@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def upload_image(request):
    f = request.FILES["file"]            # form-data key: file
    path = default_storage.save(f"uploads/{f.name}", f)
    url = default_storage.url(path)      # presigned URL(만료됨)
    return Response({"path": path, "url": url})