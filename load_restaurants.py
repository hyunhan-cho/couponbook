"""
CSV 파일에서 가게 데이터를 읽어서 DB에 넣는 스크립트
Django shell에서 실행: python manage.py shell < load_restaurants.py
또는 직접 실행: python load_restaurants.py
"""
import os
import sys
import django
from pathlib import Path

# Django 설정
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'supabase_settings')
django.setup()

import csv
from django.utils.dateparse import parse_time
from couponbook.models import LegalDistrict, Place

def load_legal_districts():
    """기본 법정동 데이터 생성 (CSV에 있는 주소만)"""
    districts = {
        ("서울", "강남구", "역삼동"),
        ("서울", "서초구", "서초동"),
        ("서울", "강동구", "성내동"),
        ("서울", "강동구", "천호동"),
        ("서울", "송파구", "풍납동"),
        ("서울", "강동구", "길동"),
        ("서울", "강동구", "둔촌동"),
        ("서울", "송파구", "송파동"),
        ("서울", "강동구", "암사동"),
        ("서울", "송파구", "신천동"),
        ("서울", "송파구", "방이동"),
    }
    
    created_count = 0
    for idx, (province, city, district) in enumerate(districts, start=1):
        province_full = f"{province}특별시" if province == "서울" else province
        code = f"11{idx:03d}00000"  # 임시 코드
        
        obj, created = LegalDistrict.objects.get_or_create(
            code_in_law=code,
            defaults={
                'province': province_full,
                'city': city,
                'district': district,
            }
        )
        if created:
            created_count += 1
            print(f"✓ LegalDistrict 생성: {province_full} {city} {district}")
    
    return created_count

def load_restaurants():
    """CSV에서 가게 데이터 로드"""
    csv_path = BASE_DIR / "restaurants - restaurants.csv.csv"
    
    if not csv_path.exists():
        print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_path}")
        return 0
    
    created_count = 0
    skipped_count = 0
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                # province 매핑 (CSV는 "서울", DB는 "서울특별시")
                province = row['province']
                province_full = f"{province}특별시" if province == "서울" else province
                
                # LegalDistrict 찾기
                try:
                    district_obj = LegalDistrict.objects.filter(
                        province=province_full,
                        city=row['city'],
                        district=row['district']
                    ).first()
                    
                    if not district_obj:
                        print(f"⚠️  법정동 없음: {province_full} {row['city']} {row['district']} - {row['name']} 스킵")
                        skipped_count += 1
                        continue
                
                except Exception as e:
                    print(f"⚠️  법정동 조회 실패: {province_full} {row['city']} {row['district']} - {e}")
                    skipped_count += 1
                    continue
                
                # 이미 존재하는 가게인지 확인
                if Place.objects.filter(
                    name=row['name'],
                    address_district=district_obj,
                    address_rest=row['address_rest']
                ).exists():
                    print(f"→ 이미 존재: {row['name']}")
                    skipped_count += 1
                    continue
                
                # Place 생성
                place = Place(
                    name=row['name'],
                    address_district=district_obj,
                    address_rest=row['address_rest'],
                    image_url=row['image_url'] if row['image_url'] else 'https://via.placeholder.com/300',
                    opens_at=parse_time(row['opens_at']),
                    closes_at=parse_time(row['closes_at']),
                    last_order=parse_time(row['last_order']),
                    tel=row['tel'] if row['tel'] else '',
                    tags=row['tags'] if row['tags'] else '',
                )
                
                # save() 호출 - 카카오맵 API로 위경도 자동 계산됨
                place.save()
                
                if place.id:  # 저장 성공
                    created_count += 1
                    print(f"✓ {created_count}. {place.name} (위도: {place.lat}, 경도: {place.lng})")
                else:
                    print(f"✗ 저장 실패: {row['name']} (카카오맵 검색 실패 가능성)")
                    skipped_count += 1
                    
            except Exception as e:
                print(f"✗ 오류 발생: {row['name']} - {e}")
                skipped_count += 1
                continue
    
    return created_count, skipped_count

if __name__ == "__main__":
    print("=" * 60)
    print("🏪 가게 데이터 로딩 시작")
    print("=" * 60)
    
    # 1. 법정동 데이터 로드
    print("\n[1단계] 법정동 데이터 생성...")
    district_count = load_legal_districts()
    print(f"✅ 법정동 {district_count}개 생성 완료\n")
    
    # 2. 가게 데이터 로드
    print("[2단계] 가게 데이터 로딩...")
    print("⚠️  카카오맵 API로 위경도를 계산하므로 시간이 걸립니다...\n")
    
    created, skipped = load_restaurants()
    
    print("\n" + "=" * 60)
    print(f"✅ 완료!")
    print(f"   - 생성된 가게: {created}개")
    print(f"   - 스킵된 가게: {skipped}개")
    print("=" * 60)

