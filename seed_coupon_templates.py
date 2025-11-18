"""
모든 Place(가게)에 대해 기본 쿠폰 템플릿과 리워드 정보를 생성하는 스크립트.

실행 방법 (프로젝트 루트에서):
    .\.venv\Scripts\python.exe seed_coupon_templates.py
"""

import os
import sys
from datetime import timedelta
from pathlib import Path

import django
from django.utils.timezone import now


BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "supabase_settings")
django.setup()

from couponbook.models import Place, CouponTemplate, RewardsInfo  # noqa: E402


def main() -> None:
    created = 0
    skipped = 0

    for place in Place.objects.all():
        if CouponTemplate.objects.filter(place=place).exists():
            print(f"→ 이미 템플릿 존재: {place.name}")
            skipped += 1
            continue

        tmpl = CouponTemplate.objects.create(
            place=place,
            valid_until=now() + timedelta(days=365),
            first_n_persons=0,
            is_on=True,
        )
        RewardsInfo.objects.create(
            coupon_template=tmpl,
            amount=10,
            reward="스탬프 10개 모으면 1회 무료 제공",
        )
        created += 1
        print(f"✓ 템플릿 생성: {tmpl.id} - {place.name}")

    print("\n==============================")
    print(f"새로 생성된 쿠폰 템플릿: {created}개")
    print(f"이미 있던 가게(스킵): {skipped}개")
    print("==============================")


if __name__ == "__main__":
    main()


