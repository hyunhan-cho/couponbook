"""Supabase(PostgreSQL)용 설정.

기본 설정은 settings_base.py 를 그대로 가져오고,
DATABASES 만 .env 값 기반으로 Postgres(Supabase)로 교체합니다.

⚠️ 기존 운영 DB와 절대 섞이지 않도록
   SUPABASE_DB_* 전용 env 키만 사용합니다.
"""

from settings_base import *
import os


# 배포 환경에서는 환경변수로 제어 (기본 False)
DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"

# MVP 단계이므로 모든 Origin 허용
ALLOWED_HOSTS = ["*"]

INTERNAL_IPS = [
    "127.0.0.1",
]

# 모든 Origin에서의 CORS 요청 허용 (MVP 전용)
CORS_ALLOW_ALL_ORIGINS = True

# CSRF 토큰 검증은 CORS_ALLOW_ALL_ORIGINS=True일 때 자동으로 완화됨
# Django는 스키마가 필요하므로 빈 리스트로 설정
CSRF_TRUSTED_ORIGINS = []


# Supabase(PostgreSQL) 데이터베이스 설정
# .env 에 필수로 넣어야 하는 값:
#   SUPABASE_DB_NAME, SUPABASE_DB_USER, SUPABASE_DB_PASSWORD, SUPABASE_DB_HOST
# 선택:
#   SUPABASE_DB_PORT (기본 5432)
#
# 👉 이렇게 하면, 기존 운영용 DB_* env 랑 절대 섞이지 않고
#    이 프로젝트 전용 Supabase DB 만 따로 붙습니다.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        # OS 환경변수 우선, 없으면 .env(config)에서 읽기
        "NAME": os.getenv("SUPABASE_DB_NAME") or config("SUPABASE_DB_NAME"),
        "USER": os.getenv("SUPABASE_DB_USER") or config("SUPABASE_DB_USER"),
        "PASSWORD": os.getenv("SUPABASE_DB_PASSWORD") or config("SUPABASE_DB_PASSWORD"),
        "HOST": os.getenv("SUPABASE_DB_HOST") or config("SUPABASE_DB_HOST"),
        "PORT": os.getenv("SUPABASE_DB_PORT") or config("SUPABASE_DB_PORT", default="5432"),
        # Supabase는 일반적으로 SSL 필요
        "OPTIONS": {"sslmode": os.getenv("SUPABASE_DB_SSLMODE", "require")},
    }
}


