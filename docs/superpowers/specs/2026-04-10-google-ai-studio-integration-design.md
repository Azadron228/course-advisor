# Spec: Google AI Studio Integration and Environment-based Model Selection

## 1. Overview
Add support for Google AI Studio (Gemini) models using `pydantic-ai`. The system should automatically select the best available model provider based on environment variables, prioritizing Google AI Studio, then OpenAI, then Ollama.

## 2. Requirements
- Support `GOOGLE_API_KEY` in `.env`.
- Support `GEMINI_MODEL_NAME` (default `gemini-1.5-flash`) in `.env`.
- Automaticaly select provider in the backend if none is explicitly requested.
- Remove provider selection from the frontend UI to keep it simple.
- Fix broken `model_provider` reference in `frontend/app.py`.

## 3. Architecture & Components

### 3.1 Data Models (`backend/models.py`)
- Add `GEMINI` and `AUTO` to `ModelProvider` enum.

### 3.2 Model Factory (`backend/agent.py`)
- Update `get_model(provider: ModelProvider)`:
    - If `provider == ModelProvider.AUTO` (default):
        1. If `GOOGLE_API_KEY` exists -> return `GeminiModel`.
        2. If `OPENAI_API_KEY` exists -> return `OpenAIModel`.
        3. If `OLLAMA_BASE_URL` exists -> return `OpenAIModel` (Ollama).
        4. Else -> return `TestModel()`.
    - If specific provider is requested, return it or fail gracefully.

### 3.3 API Layer (`backend/main.py`)
- Default `model_provider` parameter in `/recommend` to `ModelProvider.AUTO`.

### 3.4 Frontend (`frontend/app.py`)
- Remove any provider selection logic.
- Ensure `/recommend` is called without `model_provider` parameter (letting it default to `AUTO`).

## 4. Configuration (`.env.example`)
Add:
```bash
# Google AI Studio Configuration
GOOGLE_API_KEY=your-api-key-here
GEMINI_MODEL_NAME=gemini-1.5-flash
```

## 5. Testing & Validation
- **Unit Test**: Test `get_model` with mocked environment variables.
- **Integration Test**: Verify `/recommend` works when `GOOGLE_API_KEY` is provided.
