# AI Chat and Dashboard Layout Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the dashboard into a chat-centric experience with a Redis-backed AI advisor and a "Getting Started" upload flow.

**Architecture:** 
- **Backend:** Redis-backed chat history, new `/chat` endpoints, and context-aware system prompts.
- **Frontend:** Refactored Sidebar (Chat), collapsible Settings (Sliders), and conditional Main Content (Upload vs. Roadmap).

**Tech Stack:** FastAPI, Redis, SQLAlchemy (PostgreSQL), Next.js (TypeScript), Tailwind CSS, Lucide React.

---

### Task 1: Redis Chat History Service

**Files:**
- Create: `backend/app/core/redis_chat.py`
- Test: `tests/test_redis_chat.py`

- [ ] **Step 1: Create the Redis chat history service**
```python
import json
from typing import List, Dict
from arq.connections import RedisSettings
from redis.asyncio import Redis
from ..core.config import settings

class RedisChatHistory:
    def __init__(self, redis_url: str = settings.REDIS_URL):
        self.redis = Redis.from_url(redis_url, decode_responses=True)
        self.prefix = "chat_history:"
        self.max_messages = 20

    async def add_message(self, user_id: str, role: str, content: str):
        key = f"{self.prefix}{user_id}"
        message = json.dumps({"role": role, "content": content})
        await self.redis.rpush(key, message)
        await self.redis.ltrim(key, -self.max_messages, -1)
        await self.redis.expire(key, 86400) # 24 hours

    async def get_history(self, user_id: str) -> List[Dict[str, str]]:
        key = f"{self.prefix}{user_id}"
        messages = await self.redis.lrange(key, 0, -1)
        return [json.loads(m) for m in messages]

    async def clear_history(self, user_id: str):
        key = f"{self.prefix}{user_id}"
        await self.redis.delete(key)
```

- [ ] **Step 2: Write test for Redis history**
```python
import pytest
from backend.app.core.redis_chat import RedisChatHistory

@pytest.mark.asyncio
async def test_redis_chat_history():
    history = RedisChatHistory()
    user_id = "test_user@example.com"
    await history.clear_history(user_id)
    
    await history.add_message(user_id, "user", "Hello")
    await history.add_message(user_id, "assistant", "Hi there!")
    
    messages = await history.get_history(user_id)
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["content"] == "Hi there!"
    
    await history.clear_history(user_id)
    assert len(await history.get_history(user_id)) == 0
```

- [ ] **Step 3: Run test**
Run: `pytest tests/test_redis_chat.py`
Expected: PASS

- [ ] **Step 4: Commit**
```bash
git add backend/app/core/redis_chat.py tests/test_redis_chat.py
git commit -m "feat: add Redis chat history service"
```

---

### Task 2: Chat API Endpoints

**Files:**
- Modify: `backend/app/api/v1/recommendations.py`
- Modify: `backend/app/schemas/recommendation.py`
- Test: `tests/test_chat_api.py`

- [ ] **Step 1: Add Chat Schemas**
In `backend/app/schemas/recommendation.py`:
```python
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    history: List[ChatMessage]
```

- [ ] **Step 2: Implement Chat Endpoints**
In `backend/app/api/v1/recommendations.py`:
```python
from ...core.redis_chat import RedisChatHistory
from ...schemas.recommendation import ChatRequest, ChatResponse, ChatMessage

chat_history = RedisChatHistory()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_advisor(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user)
):
    user_id = current_user.email
    # 1. Get History
    history = await chat_history.get_history(user_id)
    
    # 2. Prepare LLM Call (Mocked for now or use get_model)
    # In reality, we'd use get_model(ModelProvider.AUTO)
    # system_prompt = f"You are an academic advisor for {user_id}..."
    llm_response = f"I am your advisor. You said: {request.message}" 
    
    # 3. Save to History
    await chat_history.add_message(user_id, "user", request.message)
    await chat_history.add_message(user_id, "assistant", llm_response)
    
    # 4. Return
    updated_history = await chat_history.get_history(user_id)
    return ChatResponse(response=llm_response, history=updated_history)

@router.get("/chat/history", response_model=List[ChatMessage])
async def get_chat_history(
    current_user: User = Depends(get_current_active_user)
):
    return await chat_history.get_history(current_user.email)
```

- [ ] **Step 3: Run integration test**
Run: `pytest tests/test_chat_api.py` (Create mock test first)
Expected: PASS

- [ ] **Step 4: Commit**
```bash
git add backend/app/api/v1/recommendations.py backend/app/schemas/recommendation.py
git commit -m "feat: add chat endpoints to recommendations router"
```

---

### Task 3: Dashboard Layout Refactor (Frontend)

**Files:**
- Modify: `frontend/src/app/dashboard/page.tsx`
- Modify: `frontend/src/lib/types.ts`
- Modify: `frontend/src/lib/api.ts`

- [ ] **Step 1: Update Frontend Types**
In `frontend/src/lib/types.ts`:
```typescript
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatResponse {
  response: string;
  history: ChatMessage[];
}
```

- [ ] **Step 2: Restructure Dashboard Layout**
In `frontend/src/app/dashboard/page.tsx`:
- Move `Upload` section from Sidebar to a new `WelcomeCard` in the main area.
- Add `ChatInterface` to Sidebar.
- Wrap Sliders in a `Disclosure` or `Collapsible` "Settings" section.

- [ ] **Step 3: Implement Chat UI**
```typescript
const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
const [chatInput, setChatInput] = useState('');

const handleSendMessage = async () => {
  if (!chatInput.trim()) return;
  const userMsg = chatInput;
  setChatInput('');
  setChatMessages([...chatMessages, { role: 'user', content: userMsg }]);
  
  const resp = await api.post('/api/v1/recommendations/chat', { message: userMsg });
  setChatMessages(resp.data.history);
};
```

- [ ] **Step 4: Commit**
```bash
git add frontend/src/app/dashboard/page.tsx frontend/src/lib/types.ts
git commit -m "ui: refactor dashboard layout and add chat interface"
```

---

### Task 4: Final Integration & Contextual Prompting

**Files:**
- Modify: `backend/app/api/v1/recommendations.py`
- Modify: `backend/app/agent.py` (if needed for helper)

- [ ] **Step 1: Connect Chat to LLM with Student Context**
In `backend/app/api/v1/recommendations.py`:
- Fetch student transcript if available.
- Create system prompt.
- Call LLM.

- [ ] **Step 2: Verify End-to-End**
Run the full stack and test chat in the browser.

- [ ] **Step 3: Final Commit**
```bash
git add backend/app/api/v1/recommendations.py
git commit -m "feat: complete contextual AI chat integration"
```
