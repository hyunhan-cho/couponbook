# GitHub Push 전 체크리스트

## ✅ 변경 사항
1. **CORS 설정 추가**: `http://localhost:5174`, `http://127.0.0.1:5174` 허용 (로컬/배포 모두)
2. **CSRF 설정 추가**: 로컬에 5174 포트 추가
3. **위치 데이터 파일 생성**: `modelproject/data/locations.json` (샘플 데이터)
4. **Swagger 문서 보강**: `/api/locations/` 엔드포인트에 파라미터 설명 추가
5. **Postman 컬렉션 추가**: `postman/backend_collection.postman_collection.json`
6. **.gitignore 수정**: `data/*` 제외 규칙 제거 → 위치 JSON 파일 커밋 가능

## ✅ 로컬 테스트 완료
- [x] Django 서버 실행 (local_settings, SQLite)
- [x] 회원가입/로그인 정상 동작 (`identifier` 또는 `username` 모두 사용 가능)
- [x] JWT 토큰 발급/보호 API 호출 성공
- [x] `/api/locations/` 전체/파라미터 조회 성공
- [x] Swagger UI/스키마 정상 응답 (200)

## ✅ 파일 경로 확인
- `BASE_DIR` = 프로젝트 루트 (`c:\Users\choke\backend_hackertone`)
- `locations.json` 경로: `BASE_DIR / "modelproject" / "data" / "locations.json"`
  - 실제 파일: `c:\Users\choke\backend_hackertone\modelproject\data\locations.json` ✅

## ⚠️ 배포 시 체크 사항
1. **환경변수 설정** (Cloudtype):
   - `CORS_ALLOWED_ORIGINS`: 프론트 도메인 추가 (기본값에 5174 포함됨)
   - `CSRF_TRUSTED_ORIGINS`: HTTPS 프론트 도메인 추가
   - `ALLOWED_HOSTS`: 배포 도메인 추가
   
2. **위치 데이터 업데이트** (선택):
   - 현재: 샘플 데이터 (서울/경기 일부)
   - 전국 데이터 필요 시: `create_locations.py` 실행 후 커밋

3. **Docker 빌드 확인**:
   - `COPY . .` 명령으로 `modelproject/data/locations.json` 자동 포함됨
   - 마이그레이션/정적파일 수집 자동 실행

## 📋 커밋/푸시 명령어
```powershell
cd c:\Users\choke\backend_hackertone
git add .
git commit -m "feat: Add CORS for port 5174, locations API swagger docs, and sample locations.json"
git push origin main
```

## 🧪 배포 후 테스트
```powershell
# 위치 API
Invoke-WebRequest -Uri https://port-0-couponbook-mi41xmxo46808c9c.sel3.cloudtype.app/api/locations/

# Swagger
Start-Process https://port-0-couponbook-mi41xmxo46808c9c.sel3.cloudtype.app/schema/swagger/
```
