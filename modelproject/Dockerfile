FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=modelproject.supabase_settings

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
 && rm -rf /var/lib/apt/lists/*

# pip 업그레이드
RUN pip install --upgrade pip

# requirements.txt만 먼저 복사하여 레이어 캐싱
COPY requirements.txt .

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 전체 소스 복사
COPY . .

ENV PYTHONPATH=/app

# Cloudtype 동적 포트 바인드 및 마이그레이션/정적파일 수집
CMD ["/bin/sh", "-c", \
    "SUPABASE_DB_PORT=${SUPABASE_DB_PORT_MIGRATE:-${SUPABASE_DB_PORT}} python manage.py migrate --noinput && \
     python manage.py collectstatic --noinput && \
     gunicorn --bind 0.0.0.0:${PORT:-8000} modelproject.wsgi:application"]