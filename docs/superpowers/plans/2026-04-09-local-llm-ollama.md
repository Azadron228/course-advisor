# Local LLM Integration (Ollama) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a local LLM runner (Ollama) via Docker and enable switching between OpenAI GPT and the local model in the backend and UI.

**Architecture:** 
- **Model Runner:** Ollama running in a separate Docker container.
- **Backend:** Update `backend/agent.py` to support dynamic model selection using PydanticAI's multi-model support.
- **Frontend:** Add a sidebar selection for the LLM provider.

**Tech Stack:** Docker, Ollama, PydanticAI, FastAPI, Streamlit.

---

### Task 1: Update Docker Compose

**Files:**
- Modify: `docker-compose.yml`

- [ ] **Step 1: Add Ollama service**

```yaml
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
```

- [ ] **Step 2: Update backend environment**

Add `OLLAMA_BASE_URL=http://ollama:11434` to the backend service.

---

### Task 2: Update Backend for Model Switching

**Files:**
- Modify: `backend/agent.py`
- Modify: `backend/models.py`
- Modify: `backend/scoring/rag.py`
- Modify: `backend/scoring/orchestrator.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Add ModelProvider enum to models.py**

```python
from enum import Enum

class ModelProvider(str, Enum):
    OPENAI = "openai"
    OLLAMA = "ollama"
```

- [ ] **Step 2: Update agent.py to support dynamic model selection**

Modify `recommendation_agent` to accept a model during `run()`.

- [ ] **Step 3: Update endpoints to accept model_provider**

---

### Task 3: Update Streamlit UI

**Files:**
- Modify: `frontend/app.py`

- [ ] **Step 1: Add model selector to sidebar**

- [ ] **Step 2: Pass selected model to backend API**

---
