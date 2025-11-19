"""
쿠폰 템플릿 리스트 시리얼라이저 동작을 로컬에서 직접 확인하는 디버그 스크립트.

실행:
    .\.venv\Scripts\python.exe debug_coupon_templates.py
"""

import os
import sys
from pathlib import Path

import django
from django.utils.timezone import now


BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "supabase_settings")
django.setup()

from rest_framework.test import APIRequestFactory  # noqa: E402

from django.db import models  # noqa: E402
from couponbook.models import CouponTemplate  # noqa: E402
from couponbook.serializers import (  # noqa: E402
    CouponTemplateListSerializer,
)


def main() -> None:
    factory = APIRequestFactory()
    # 실제 브라우저와 비슷하게 Host 헤더를 넣어 DisallowedHost를 피함
    request = factory.get(
        "/couponbook/coupon-templates/", HTTP_HOST="127.0.0.1:8000"
    )

    qs = CouponTemplate.objects.select_related(
        "place", "place__address_district"
    ).filter(is_on=True).filter(
        (models.Q(valid_until__isnull=True) | models.Q(valid_until__gte=now()))
    )

    print(f"쿠폰 템플릿 개수: {qs.count()}")

    serializer = CouponTemplateListSerializer(
        qs, many=True, context={"request": request}
    )
    data = serializer.data
    print(f"직렬화 완료, 첫 1개만 출력:")
    if data:
        print(data[0])
    else:
        print("데이터 없음")


if __name__ == "__main__":
    main()


