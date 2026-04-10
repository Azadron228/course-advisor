# Google AI Studio Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Gemini support and implement automatic model provider selection based on environment variables.

**Architecture:** Update `ModelProvider` enum, enhance `get_model` factory with priority logic (Gemini > OpenAI > Ollama), and refactor API/Frontend to use this "AUTO" selection by default.

**Tech Stack:** Python, FastAPI, PydanticAI, Streamlit.

---

### Task 1: Data Model and Configuration

**Files:**
- Modify: `backend/models.py`
- Modify: `.env.example`

- [ ] **Step 1: Update ModelProvider Enum**

```python
# backend/models.py
class ModelProvider(str, Enum):
    OPENAI = "openai"
    OLLAMA = "ollama"
    GEMINI = "gemini"
    AUTO = "auto"
```

- [ ] **Step 2: Update .env.example**

```bash
# .env.example
# Google AI Studio Configuration
GOOGLE_API_KEY=your-api-key-here
GEMINI_MODEL_NAME=gemini-1.5-flash
```

- [ ] **Step 3: Commit**

```bash
git add backend/models.py .env.example
git commit -m "feat: add GEMINI and AUTO providers to model and config"
```

---

### Task 2: Implement Gemini Support and Auto-Selection

**Files:**
- Modify: `backend/agent.py`

- [ ] **Step 1: Update Imports and Implement Factory Logic**

```python
# backend/agent.py
import os
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.gemini import GeminiModel # Add this
from pydantic import BaseModel, Field
from  models import ModelProvider

# ... (AgentRecommendation class remains same)

def get_model(provider: ModelProvider = ModelProvider.AUTO):
    # Auto-detection logic
    if provider == ModelProvider.AUTO:
        if os.getenv("GOOGLE_API_KEY"):
            provider = ModelProvider.GEMINI
        elif os.getenv("OPENAI_API_KEY"):
            provider = ModelProvider.OPENAI
        elif os.getenv("OLLAMA_BASE_URL"):
            provider = ModelProvider.OLLAMA
        else:
            return TestModel()

    if provider == ModelProvider.GEMINI:
        return GeminiModel(
            model_name=os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash"),
            api_key=os.getenv("GOOGLE_API_KEY"),
        )

    if provider == ModelProvider.OLLAMA:
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return OpenAIModel(
            model_name='llama3',
            base_url=f"{base_url}/v1",
            api_key='ollama',
        )
    
    if provider == ModelProvider.OPENAI:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return TestModel()
        return OpenAIModel('gpt-4o', api_key=api_key)

    return TestModel()
```

- [ ] **Step 2: Commit**

```bash
git add backend/agent.py
git commit -m "feat: implement Gemini support and priority-based model selection"
```

---

### Task 3: API and Frontend Refactoring

**Files:**
- Modify: `backend/main.py`
- Modify: `frontend/app.py`

- [ ] **Step 1: Update Backend Endpoint Default**

```python
# backend/main.py
@app.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(
    student: Student, 
    preference: UserPreference,
    model_provider: ModelProvider = ModelProvider.AUTO # Change default to AUTO
):
    # ...
```

- [ ] **Step 2: Clean up Frontend and Fix API call**

Remove any local `model_provider` definitions and ensure the call to `/recommend` doesn't pass it (or passes it as `auto`).

```python
# frontend/app.py
# Remove any 'model_provider' variable if it was defined globally or locally.
# Update the POST request:

                    rec_resp = httpx.post(
                        f"{BACKEND_URL}/recommend", 
                        # Remove params={"model_provider": model_provider}
                        json={"student": student_data, "preference": pref_data}, 
                        timeout=60.0 
                    )
```

- [ ] **Step 3: Commit**

```bash
git add backend/main.py frontend/app.py
git commit -m "refactor: default to AUTO provider and fix frontend API call"
```

---

### Task 4: Testing and Validation

**Files:**
- Create: `tests/test_agent_factory.py`

- [ ] **Step 1: Write Factory Tests**

```python
# tests/test_agent_factory.py
import os
import unittest
from unittest.mock import patch
from  agent import get_model
from  models import ModelProvider
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.test import TestModel

class TestAgentFactory(unittest.TestCase):
    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test_google_key"})
    def test_get_model_auto_prefers_gemini(self):
        model = get_model(ModelProvider.AUTO)
        self.assertIsInstance(model, GeminiModel)

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_openai_key"}, clear=True)
    def test_get_model_auto_falls_back_to_openai(self):
        # Ensure GOOGLE_API_KEY is not set
        model = get_model(ModelProvider.AUTO)
        self.assertIsInstance(model, OpenAIModel)
        self.assertEqual(model.model_name, 'gpt-4o')

    @patch.dict(os.environ, {}, clear=True)
    def test_get_model_auto_fallback_to_test(self):
        model = get_model(ModelProvider.AUTO)
        self.assertIsInstance(model, TestModel)

if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Run Tests**

Run: `pytest tests/test_agent_factory.py`
Expected: PASS

- [ ] **Step 3: Final Commit**

```bash
git add tests/test_agent_factory.py
git commit -m "test: add agent factory unit tests"
```
