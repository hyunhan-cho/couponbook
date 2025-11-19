## 쿠폰 & AI 추천 연동 플로우

- **Base URL**: `https://port-0-couponbook-mi41xmxo46808c9c.sel3.cloudtype.app`
- **인증**: 대부분 `Authorization: Bearer {accessToken}` 필요

---

## 0. 선행 조건

### 0-1. 로그인

- **Endpoint**
  - `POST /accounts/auth/login/`
- **Body**
  ```json
  { "identifier": "alice", "password": "P@ssw0rd!" }
  ```
- **Response**
  ```json
  { "access": "...", "refresh": "..." }
  ```

### 0-2. 내 쿠폰북 ID 가져오기

- **Endpoint**
  - `GET /couponbook/own-couponbook/`
- **Header**
  - `Authorization: Bearer {accessToken}`
- **Response 예**
  ```json
  { "id": 1, "user": 1, "created_at": "..." }
  ```
- 이후 호출에서 `couponbook_id = 1` 사용

---

## 1. 쿠폰 템플릿 조회

### 1-1. 전체/검색 템플릿 목록

- **Endpoint**
  - `GET /couponbook/coupon-templates/`
  - 인증: 불필요

- **Query 예시**
  - 특정 동 필터:
    - `/couponbook/coupon-templates/?district=역삼동`
  - 가게 이름 검색:
    - `/couponbook/coupon-templates/?name=스타벅스`
  - 복합:
    - `/couponbook/coupon-templates/?district=역삼동&name=스타벅스`

- **Response 예**
  ```json
  [
    {
      "id": 1,
      "place": {
        "id": 1,
        "name": "스타벅스 강남점",
        "address_province": "서울특별시",
        "address_city": "강남구",
        "address_district": "역삼동",
        "phone": "02-1234-5678"
      },
      "name": "커피 10잔 쿠폰",
      "description": "커피 10잔 구매 시 1잔 무료",
      "max_stamps": 10,
      "reward": "아메리카노 1잔 무료",
      "valid_until": "2025-12-31",
      "is_on": true
    }
  ]
  ```

### 1-2. AI 추천 템플릿 목록

- **Endpoint**
  - `GET /couponbook/own-couponbook/curation/`
  - Header: `Authorization: Bearer {accessToken}`

- **설명**
  - 현재 유저의 보유 쿠폰/패턴/선호 지역을 기반으로 **AI 큐레이션된 템플릿 목록**만 반환
  - 이미 보유한 템플릿은 제외됨
  - ⚠️ OPENAI_API_KEY 환경변수 필요 (없으면 상위 3개 반환)

- **Response 예**
  ```json
  [
    {
      "id": 15,
      "place": {
        "id": 5,
        "name": "올리브영 강남점",
        "address_province": "서울특별시",
        "address_city": "강남구",
        "address_district": "역삼동"
      },
      "name": "뷰티 제품 10개 쿠폰",
      "description": "뷰티 제품 10개 구매 시 10% 할인",
      "max_stamps": 10,
      "reward": "10% 할인 쿠폰",
      "valid_until": "2025-12-31"
    }
  ]
  ```

### 1-3. 단일 템플릿 상세 조회

- **Endpoint**
  - `GET /couponbook/coupon-templates/{coupon_template_id}/`
  - Header: `Authorization: Bearer {accessToken}`

- **Response 예**
  ```json
  {
    "id": 1,
    "place": {
      "id": 1,
      "name": "스타벅스 강남점",
      "address_province": "서울특별시",
      "address_city": "강남구",
      "address_district": "역삼동",
      "address_detail": "테헤란로 123",
      "phone": "02-1234-5678"
    },
    "name": "커피 10잔 쿠폰",
    "description": "커피 10잔 구매 시 1잔 무료",
    "max_stamps": 10,
    "reward": "아메리카노 1잔 무료",
    "valid_until": "2025-12-31"
  }
  ```

---

## 2. 템플릿 → 내 쿠폰북에 쿠폰 등록

### 2-1. 쿠폰 생성 (템플릿 기반)

- **Endpoint**
  - `POST /couponbook/couponbooks/{couponbook_id}/coupons/`
  - Header: `Authorization: Bearer {accessToken}`

- **Request Body 예**
  ```json
  {
    "original_template": 1
  }
  ```

- **Response 예 (201 Created)**
  ```json
  {
    "id": 3,
    "original_template": 1,
    "place_name": "스타벅스 강남점",
    "place_address": "서울특별시 강남구 역삼동",
    "stamp_counts": 0,
    "max_stamps": 10,
    "reward": "아메리카노 1잔 무료",
    "saved_at": "2025-01-15T12:30:00Z",
    "expires_at": "2025-12-31T23:59:59Z",
    "is_expired": false
  }
  ```

- **에러 예**
  ```json
  { "detail": "이미 등록된 쿠폰 템플릿입니다." }
  ```

---

## 3. 내 쿠폰 목록 / 상세

### 3-1. 내 쿠폰 목록 조회

- **Endpoint**
  - `GET /couponbook/couponbooks/{couponbook_id}/coupons/`
  - Header: `Authorization: Bearer {accessToken}`

- **Query 옵션**
  - `address`: 가게 주소(부분 일치)
  - `district`: 법정동 (정확 일치)
  - `name`: 가게 이름
  - `is_expired`: `true` / `false`
  - `is_open`: `true` / `false`
  - `ordering`: `stamp_counts` or `-stamp_counts`

- **예시**
  - `/couponbook/couponbooks/1/coupons/?district=역삼동&ordering=-stamp_counts`

- **Response 예**
  ```json
  [
    {
      "id": 1,
      "original_template": 1,
      "place_name": "스타벅스 강남점",
      "place_address": "서울특별시 강남구 역삼동",
      "stamp_counts": 7,
      "max_stamps": 10,
      "reward": "아메리카노 1잔 무료",
      "saved_at": "2025-01-01T00:00:00Z",
      "expires_at": "2025-12-31T23:59:59Z",
      "is_expired": false
    }
  ]
  ```

### 3-2. 단일 쿠폰 상세

- **Endpoint**
  - `GET /couponbook/coupons/{coupon_id}/`
  - Header: `Authorization: Bearer {accessToken}`

- **Response 예**
  ```json
  {
    "id": 1,
    "original_template": 1,
    "place": {
      "id": 1,
      "name": "스타벅스 강남점",
      "address_province": "서울특별시",
      "address_city": "강남구",
      "address_district": "역삼동",
      "address_detail": "테헤란로 123",
      "phone": "02-1234-5678"
    },
    "stamp_counts": 7,
    "max_stamps": 10,
    "reward": "아메리카노 1잔 무료",
    "description": "커피 10잔 구매 시 1잔 무료",
    "saved_at": "2025-01-01T00:00:00Z",
    "expires_at": "2025-12-31T23:59:59Z",
    "stamps": [
      { "id": 1, "stamped_at": "2025-01-02T10:30:00Z" },
      { "id": 2, "stamped_at": "2025-01-05T14:20:00Z" }
    ]
  }
  ```

### 3-3. 쿠폰 삭제

- **Endpoint**
  - `DELETE /couponbook/coupons/{coupon_id}/`
  - Header: `Authorization: Bearer {accessToken}`

- **Response**
  - `204 No Content`

- **주의**
  - 본인의 쿠폰만 삭제 가능합니다

---

## 4. 스탬프 적립

### 4-1. 스탬프 추가

- **Endpoint**
  - `POST /couponbook/coupons/{coupon_id}/stamps/`
  - Header: `Authorization: Bearer {accessToken}`

- **Request Body 예**
  ```json
  {
    "receipt": "00000001"
  }
  ```

- **Response 예 (201 Created)**
  ```json
  {
    "id": 10,
    "coupon": 1,
    "receipt": "00000001",
    "customer": {
      "id": 1,
      "username": "alice"
    },
    "stamped_at": "2025-01-15T14:30:00Z"
  }
  ```

- **에러 예**
  ```json
  { "detail": "이미 사용된 영수증 번호입니다." }
  ```
  ```json
  { "detail": "존재하지 않는 영수증 번호입니다." }
  ```

---

## 5. 즐겨찾기 (선택)

### 5-1. 즐겨찾기 추가

- **Endpoint**
  - `POST /couponbook/couponbooks/{couponbook_id}/favorites/`
  - Header: `Authorization: Bearer {accessToken}`

- **Request Body**
  ```json
  {
    "coupon": 1
  }
  ```

- **Response 예 (201 Created)**
  ```json
  {
    "id": 3,
    "coupon": 1,
    "added_at": "2025-01-15T14:30:00Z"
  }
  ```

### 5-2. 즐겨찾기 목록

- **Endpoint**
  - `GET /couponbook/couponbooks/{couponbook_id}/favorites/`
  - Header: `Authorization: Bearer {accessToken}`

- **Response 예**
  ```json
  [
    {
      "id": 1,
      "coupon": {
        "id": 1,
        "place_name": "스타벅스 강남점",
        "place_address": "서울특별시 강남구 역삼동",
        "stamp_counts": 7,
        "max_stamps": 10,
        "reward": "아메리카노 1잔 무료"
      },
      "added_at": "2025-01-10T00:00:00Z"
    }
  ]
  ```

### 5-3. 즐겨찾기 삭제

- **Endpoint**
  - `DELETE /couponbook/own-couponbook/favorites/{favorite_id}/`
  - Header: `Authorization: Bearer {accessToken}`

- **Response**
  - `204 No Content`

- **설명**
  - `favorite_id`는 즐겨찾기 목록 조회에서 받은 각 항목의 `id` 값입니다 (쿠폰 id가 아님 주의!)

---

## 📌 URL 요약표

| 기능 | 메서드 | 엔드포인트 | 인증 |
|------|--------|-----------|------|
| **쿠폰북** |
| 내 쿠폰북 조회 | GET | `/couponbook/own-couponbook/` | ✅ |
| **템플릿** |
| 템플릿 목록 | GET | `/couponbook/coupon-templates/` | ❌ |
| 템플릿 상세 | GET | `/couponbook/coupon-templates/{template_id}/` | ✅ |
| AI 추천 | GET | `/couponbook/own-couponbook/curation/` | ✅ |
| **쿠폰** |
| 쿠폰 목록 | GET | `/couponbook/couponbooks/{couponbook_id}/coupons/` | ✅ |
| 쿠폰 생성 | POST | `/couponbook/couponbooks/{couponbook_id}/coupons/` | ✅ |
| 쿠폰 상세 | GET | `/couponbook/coupons/{coupon_id}/` | ✅ |
| 쿠폰 삭제 | DELETE | `/couponbook/coupons/{coupon_id}/` | ✅ |
| **스탬프** |
| 스탬프 적립 | POST | `/couponbook/coupons/{coupon_id}/stamps/` | ✅ |
| **즐겨찾기** |
| 즐겨찾기 목록 | GET | `/couponbook/couponbooks/{couponbook_id}/favorites/` | ✅ |
| 즐겨찾기 추가 | POST | `/couponbook/couponbooks/{couponbook_id}/favorites/` | ✅ |
| 즐겨찾기 삭제 | DELETE | `/couponbook/own-couponbook/favorites/{favorite_id}/` | ✅ |
| **AI 챗봇** |
| AI 대화 | POST | `/couponbook/chat/` | ✅ |
| 추천 질문 | GET | `/couponbook/chat/` | ✅ |

---

## 🚨 중요 포인트

### 1. URL 주의사항
- **쿠폰북 조회**: `/own-couponbook/` (단수, own 포함)
- **쿠폰 목록/생성**: `/couponbooks/{id}/coupons/` (복수형 couponbooks)
- **즐겨찾기 목록/추가**: `/couponbooks/{id}/favorites/` (복수형 couponbooks)
- **즐겨찾기 삭제**: `/own-couponbook/favorites/{id}/` (단수, own 포함)
- **템플릿**: `/coupon-templates/` (하이픈 포함)

### 2. ID 구분
- `couponbook_id`: 쿠폰북의 ID (내 쿠폰북 조회에서 획득)
- `coupon_id`: 개별 쿠폰의 ID
- `favorite_id`: 즐겨찾기 항목의 ID (⚠️ 쿠폰 ID와 다름!)
- `coupon_template_id`: 템플릿의 ID

### 3. 프론트엔드 예시 코드

```javascript
// 1. 로그인 후 쿠폰북 ID 저장
const { data: couponbook } = await axios.get('/couponbook/own-couponbook/');
const couponbookId = couponbook.id; // 예: 1

// 2. 템플릿 목록 조회
const { data: templates } = await axios.get('/couponbook/coupon-templates/?district=역삼동');

// 3. 쿠폰 생성
await axios.post(`/couponbook/couponbooks/${couponbookId}/coupons/`, {
  original_template: templates[0].id
});

// 4. 내 쿠폰 목록
const { data: coupons } = await axios.get(`/couponbook/couponbooks/${couponbookId}/coupons/`);

// 5. 즐겨찾기 추가
const { data: favorite } = await axios.post(
  `/couponbook/couponbooks/${couponbookId}/favorites/`,
  { coupon: coupons[0].id }
);

// 6. 즐겨찾기 삭제 (⚠️ favorite.id 사용!)
await axios.delete(`/couponbook/own-couponbook/favorites/${favorite.id}/`);

// 7. 스탬프 적립
await axios.post(`/couponbook/coupons/${coupons[0].id}/stamps/`, {
  receipt: '00000001'
});

// 8. AI 챗봇 - 추천 질문 가져오기
const { data: suggestionsData } = await axios.get('/couponbook/chat/');
console.log(suggestionsData.suggestions); // ["내 쿠폰 몇 개야?", ...]

// 9. AI 챗봇 - 질문하기
const { data: chatResponse } = await axios.post('/couponbook/chat/', {
  message: '내 쿠폰 몇 개야?'
});
console.log(chatResponse.response); // "현재 3개의 쿠폰을 보유하고 있어!..."
console.log(chatResponse.suggestions); // 다음 추천 질문들

// 10. AI 챗봇 - 대화 이어가기 (히스토리 유지)
const conversationHistory = [
  { role: 'user', content: '내 쿠폰 몇 개야?' },
  { role: 'assistant', content: chatResponse.response }
];
const { data: nextResponse } = await axios.post('/couponbook/chat/', {
  message: '그럼 근처에 카페 더 있어?',
  conversation_history: conversationHistory
});
```

---

## 🤖 6. AI 어시스턴트 챗봇 (NEW!)

### 6-1. AI와 대화하기

- **Endpoint**
  - `POST /couponbook/chat/`
  - Header: `Authorization: Bearer {accessToken}`

- **설명**
  - 쿠폰북 AI 어시스턴트와 대화
  - 사용자의 보유 쿠폰, 선호 지역, 주변 가게 정보를 기반으로 답변
  - 친근한 반말체로 응답
  - ⚠️ OPENAI_API_KEY 환경변수 필요

- **Request Body 예**
  ```json
  {
    "message": "내 쿠폰 몇 개야?"
  }
  ```

- **Response 예 (200 OK)**
  ```json
  {
    "response": "현재 3개의 쿠폰을 보유하고 있어! 스타벅스, 맘스터치, 올리브영 쿠폰이야 ☕ 스타벅스 쿠폰이 거의 다 모였네, 스탬프 7개 중에 10개를 모으면 돼!",
    "context_used": true,
    "suggestions": [
      "스탬프 많이 모은 쿠폰 알려줘",
      "근처 카페 추천해줘",
      "즐겨찾기는 뭐야?"
    ]
  }
  ```

- **대화 히스토리 유지 (선택)**
  ```json
  {
    "message": "그럼 근처에 카페 더 있어?",
    "conversation_history": [
      {"role": "user", "content": "내 쿠폰 몇 개야?"},
      {"role": "assistant", "content": "현재 3개의 쿠폰을 보유하고 있어!..."}
    ]
  }
  ```

### 6-2. 추천 질문 가져오기

- **Endpoint**
  - `GET /couponbook/chat/`
  - Header: `Authorization: Bearer {accessToken}`

- **설명**
  - 사용자가 물어볼 만한 질문 예시를 제공
  - 채팅 UI에 버튼으로 표시 권장

- **Response 예 (200 OK)**
  ```json
  {
    "suggestions": [
      "내가 가진 쿠폰 보여줘",
      "내 쿠폰 몇 개야?",
      "스탬프 많이 모은 쿠폰 알려줘",
      "근처 카페 추천해줘",
      "역삼동에 뭐 있어?"
    ]
  }
  ```

### 6-3. 질문 예시

**쿠폰 관련:**
- "내 쿠폰 몇 개야?"
- "스타벅스 쿠폰 있어?"
- "스탬프 많이 모은 쿠폰 알려줘"
- "곧 만료되는 쿠폰 있어?"

**추천 관련:**
- "근처 카페 추천해줘"
- "역삼동 맛집 알려줘"
- "저녁 먹을 곳 추천해줘"

**사용법 관련:**
- "스탬프 적립은 어떻게 해?"
- "즐겨찾기는 뭐야?"
- "쿠폰 어떻게 사용해?"

---


