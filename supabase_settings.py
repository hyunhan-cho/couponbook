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

# ALLOWED_HOSTS/CORS/CSRF는 배포 도메인에 맞춰 환경변수로 설정 가능
ALLOWED_HOSTS = [h for h in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h]

INTERNAL_IPS = [
    "127.0.0.1",
]

CORS_ALLOWED_ORIGINS = [o for o in os.getenv(
    "CORS_ALLOWED_ORIGINS",
    (
        "http://localhost:3000,"
        "http://127.0.0.1:3000,"
        "http://localhost:5173,"
        "http://127.0.0.1:5173,"
        "http://localhost:5174,"
        "http://127.0.0.1:5174"
    )
).split(",") if o]

# CSRF 신뢰 도메인 (https 스킴 포함 필요)
CSRF_TRUSTED_ORIGINS = [o for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o]


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


