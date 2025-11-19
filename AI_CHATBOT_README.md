# 🤖 쿠폰북 AI 어시스턴트 챗봇

## 📌 개요

쿠폰북 앱에 **대화형 AI 어시스턴트**를 추가했습니다!
사용자가 자연어로 질문하면, AI가 개인화된 답변을 제공합니다.

### 주요 기능
- 💬 자연스러운 대화형 인터페이스
- 📊 사용자 쿠폰 정보 기반 개인화 답변
- 🗺️ 주변 가게/쿠폰 추천
- 📚 앱 사용법 안내
- 🔄 대화 히스토리 유지 가능

---

## 🚀 빠른 시작

### 1. API 키 설정

`.env` 파일에 OpenAI API 키를 추가하세요:

```bash
OPENAI_API_KEY=sk-proj-...
```

> 💡 API 키가 없으면 fallback 메시지가 반환됩니다.

### 2. API 엔드포인트

#### POST /couponbook/chat/ - AI와 대화

**Request:**
```json
{
  "message": "내 쿠폰 몇 개야?"
}
```

**Response:**
```json
{
  "response": "현재 3개의 쿠폰을 보유하고 있어! 스타벅스, 맘스터치, 올리브영 쿠폰이야 ☕",
  "context_used": true,
  "suggestions": [
    "스탬프 많이 모은 쿠폰 알려줘",
    "근처 카페 추천해줘"
  ]
}
```

#### GET /couponbook/chat/ - 추천 질문 목록

**Response:**
```json
{
  "suggestions": [
    "내 쿠폰 몇 개야?",
    "스탬프 많이 모은 쿠폰 알려줘",
    "근처 카페 추천해줘"
  ]
}
```

---

## 💡 질문 예시

### 쿠폰 관련
- "내 쿠폰 몇 개야?"
- "스타벅스 쿠폰 있어?"
- "스탬프 많이 모은 쿠폰 알려줘"
- "곧 만료되는 쿠폰 있어?"
- "완성 가능한 쿠폰 보여줘"

### 추천 관련
- "근처 카페 추천해줘"
- "역삼동 맛집 알려줘"
- "저녁 먹을 곳 추천해줘"
- "새로운 가게 추천해줘"

### 사용법 관련
- "스탬프 적립은 어떻게 해?"
- "즐겨찾기는 뭐야?"
- "쿠폰 어떻게 사용해?"
- "이 앱 어떻게 쓰는 거야?"

---

## 🎨 프론트엔드 구현 예시

### React 예시

```jsx
import { useState, useEffect } from 'react';
import axios from 'axios';

function ChatBot() {
  const [message, setMessage] = useState('');
  const [conversation, setConversation] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);

  // 추천 질문 가져오기
  useEffect(() => {
    axios.get('/couponbook/chat/').then(res => {
      setSuggestions(res.data.suggestions);
    });
  }, []);

  // 메시지 전송
  const sendMessage = async (text) => {
    setLoading(true);
    
    // 대화 히스토리 구성
    const history = conversation.map(msg => ({
      role: msg.sender === 'user' ? 'user' : 'assistant',
      content: msg.text
    }));

    try {
      const response = await axios.post('/couponbook/chat/', {
        message: text,
        conversation_history: history
      });

      // 대화에 추가
      setConversation([
        ...conversation,
        { sender: 'user', text },
        { sender: 'assistant', text: response.data.response }
      ]);

      // 새로운 추천 질문 업데이트
      setSuggestions(response.data.suggestions);
      setMessage('');
    } catch (error) {
      console.error('챗봇 오류:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chatbot">
      {/* 대화 내역 */}
      <div className="conversation">
        {conversation.map((msg, i) => (
          <div key={i} className={`message ${msg.sender}`}>
            {msg.text}
          </div>
        ))}
      </div>

      {/* 추천 질문 버튼 */}
      <div className="suggestions">
        {suggestions.map((sug, i) => (
          <button key={i} onClick={() => sendMessage(sug)}>
            {sug}
          </button>
        ))}
      </div>

      {/* 입력창 */}
      <div className="input-area">
        <input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage(message)}
          placeholder="무엇이든 물어보세요..."
          disabled={loading}
        />
        <button onClick={() => sendMessage(message)} disabled={loading}>
          {loading ? '전송중...' : '전송'}
        </button>
      </div>
    </div>
  );
}
```

### Vue 예시

```vue
<template>
  <div class="chatbot">
    <!-- 대화 내역 -->
    <div class="conversation">
      <div v-for="(msg, i) in conversation" :key="i" :class="`message ${msg.sender}`">
        {{ msg.text }}
      </div>
    </div>

    <!-- 추천 질문 -->
    <div class="suggestions">
      <button v-for="(sug, i) in suggestions" :key="i" @click="sendMessage(sug)">
        {{ sug }}
      </button>
    </div>

    <!-- 입력창 -->
    <div class="input-area">
      <input
        v-model="message"
        @keyup.enter="sendMessage(message)"
        placeholder="무엇이든 물어보세요..."
        :disabled="loading"
      />
      <button @click="sendMessage(message)" :disabled="loading">
        {{ loading ? '전송중...' : '전송' }}
      </button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      message: '',
      conversation: [],
      suggestions: [],
      loading: false
    };
  },
  
  mounted() {
    this.fetchSuggestions();
  },
  
  methods: {
    async fetchSuggestions() {
      const { data } = await axios.get('/couponbook/chat/');
      this.suggestions = data.suggestions;
    },
    
    async sendMessage(text) {
      if (!text.trim()) return;
      
      this.loading = true;
      const history = this.conversation.map(msg => ({
        role: msg.sender === 'user' ? 'user' : 'assistant',
        content: msg.text
      }));

      try {
        const { data } = await axios.post('/couponbook/chat/', {
          message: text,
          conversation_history: history
        });

        this.conversation.push(
          { sender: 'user', text },
          { sender: 'assistant', text: data.response }
        );

        this.suggestions = data.suggestions;
        this.message = '';
      } catch (error) {
        console.error('챗봇 오류:', error);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
```

---

## 🔧 커스터마이징

### 1. AI 응답 스타일 변경

`couponbook/chat_assistant.py`의 `system_prompt` 수정:

```python
system_prompt = """
당신은 '쿠폰북' 앱의 친절한 AI 어시스턴트입니다.

**답변 규칙:**
- 존댓말로 정중하게 대화하세요  # 반말 → 존댓말
- 이모지를 적절히 사용하세요
- 간결하고 명확하게 답변하세요
...
"""
```

### 2. GPT 모델 변경

더 빠른 응답이 필요하면 `gpt-3.5-turbo`, 더 정확한 답변이 필요하면 `gpt-4o`:

```python
response = self.client.chat.completions.create(
    model="gpt-4o",  # gpt-4o-mini → gpt-4o
    messages=messages,
    temperature=0.7,
    max_tokens=500
)
```

### 3. 추천 질문 커스터마이징

`get_quick_suggestions()` 메서드 수정:

```python
def get_quick_suggestions(self) -> list[str]:
    suggestions = [
        "내 쿠폰 보여줘",
        "오늘 뭐 먹을까?",
        "스탬프 현황 알려줘",
        # 원하는 질문 추가
    ]
    return suggestions
```

---

## ⚠️ 주의사항

### 1. API 키 비용
- OpenAI API는 사용량에 따라 과금됩니다
- `gpt-4o-mini` 모델 사용 권장 (저렴함)
- 프로덕션에서는 rate limiting 구현 권장

### 2. 에러 처리
- API 키가 없으면 fallback 메시지 반환
- OpenAI API 장애 시 안전한 에러 메시지
- 사용자 데이터 없어도 정상 동작

### 3. 보안
- 민감한 사용자 정보는 AI에 전달하지 않음
- 전화번호, 상세 주소 등은 제외됨
- API 키는 환경변수로 안전하게 관리

---

## 📊 AI가 사용하는 컨텍스트

AI 어시스턴트는 다음 정보를 기반으로 답변합니다:

```json
{
  "사용자명": "alice",
  "보유_쿠폰": [
    {
      "가게명": "스타벅스 강남점",
      "주소": "서울특별시 강남구 역삼동",
      "쿠폰명": "커피 10잔 쿠폰",
      "현재_스탬프": 7,
      "필요_스탬프": 10,
      "리워드": "아메리카노 1잔 무료",
      "태그": ["카페", "디저트"]
    }
  ],
  "선호_지역": [
    {
      "광역시도": "서울특별시",
      "시군구": "강남구",
      "법정동": "역삼동"
    }
  ],
  "주변_이용가능_쿠폰": [
    {
      "가게명": "올리브영 강남점",
      "주소": "서울특별시 강남구 역삼동",
      "쿠폰명": "뷰티 제품 10개 쿠폰",
      "필요_스탬프": 10,
      "리워드": "10% 할인 쿠폰",
      "태그": ["뷰티", "생활용품"]
    }
  ]
}
```

---

## 🎯 해커톤 데모 시나리오

### 시나리오 1: 초보 사용자
1. "이 앱 어떻게 쓰는 거야?"
2. AI: 쿠폰 저장, 스탬프 적립 방법 설명
3. "쿠폰 저장은 어떻게 해?"
4. AI: 구체적인 사용법 안내

### 시나리오 2: 쿠폰 관리
1. "내 쿠폰 몇 개야?"
2. AI: 보유 쿠폰 목록 안내
3. "스탬프 많이 모은 거 알려줘"
4. AI: 완성 임박한 쿠폰 추천

### 시나리오 3: 맛집 추천
1. "근처 맛집 추천해줘"
2. AI: 주변 가게 + 쿠폰 정보 제공
3. "카페는?"
4. AI: 카페만 필터링해서 추천

---

## 🐛 트러블슈팅

### Q: "AI 어시스턴트 기능이 현재 사용 불가능합니다" 메시지가 뜹니다.
**A:** `.env` 파일에 `OPENAI_API_KEY` 설정 확인

### Q: 응답이 너무 느립니다.
**A:** `gpt-4o-mini` 모델 사용 확인, `max_tokens` 값 줄이기

### Q: 엉뚱한 답변을 합니다.
**A:** `temperature` 값을 0.7 → 0.3으로 낮추기

### Q: 비용이 많이 나옵니다.
**A:** `max_tokens` 제한, rate limiting 구현, 캐싱 고려

---

## 📝 라이센스

이 프로젝트는 쿠폰북 앱의 일부입니다.

