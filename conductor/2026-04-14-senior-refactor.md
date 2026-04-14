# Senior Refactor: Clean FastAPI Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the backend into a cohesive, production-ready FastAPI project following senior engineering standards while avoiding overengineering.

**Architecture:**
- **Modular Routers**: Use `APIRouter` to separate auth, parsing, and recommendations.
- **Dependency Injection**: Use standard FastAPI dependency patterns for DB and Auth.
- **Config Management**: Centralize settings using `pydantic-settings`.
- **Clear Separation**: Separate SQLAlchemy ORM models from Pydantic schemas.
- **Async Throughout**: Ensure all I/O bound operations are async.

**Tech Stack:** FastAPI, SQLAlchemy 2.0 (PostgreSQL), Pydantic 2.0, Alembic, arq.

---

### Task 1: Core Configuration and Security

**Files:**
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/security.py`

- [ ] **Step 1: Implement Settings Class**
Define a `Settings` class using `BaseSettings` for env-based configuration. Include Redis settings for arq.

- [ ] **Step 2: Migrate Security Helpers**
Move JWT and password hashing functions from `auth.py` to `core/security.py`. Use the new `Settings` for secrets.

- [ ] **Step 3: Commit**
```bash
git add backend/app/core/
git commit -m "feat: add core configuration and security modules"
```

---

### Task 2: Models and Schemas Separation (with DTOs)

**Files:**
- Create: `backend/app/schemas/` (directory)
- Create: `backend/app/schemas/user.py`
- Create: `backend/app/schemas/course.py`
- Create: `backend/app/schemas/recommendation.py`
- Create: `backend/app/schemas/token.py`
- Create: `backend/app/schemas/internal.py` (Lightweight DTOs)
- Modify: `backend/app/models.py`

- [ ] **Step 1: Implement DTO Pattern in Schemas**
Separate Pydantic models into specialized schemas for different use cases:
  - **Request DTOs**: Strict validation schemas for incoming API data (e.g., `UserCreate`).
  - **Response DTOs**: Schemas for outgoing API data, using `from_attributes=True` for ORM compatibility (e.g., `UserPublic`).
  - **Internal DTOs (`internal.py`)**: Lightweight Pydantic models (with minimal validation) for passing data between internal service layers (scorers, agents, tasks). These decouple the business logic from API contracts.

- [ ] **Step 2: Clean up Models**
Keep only SQLAlchemy ORM models in `models.py`. Ensure they don't depend on Pydantic schemas.

- [ ] **Step 3: Commit**
```bash
git add backend/app/models.py backend/app/schemas/
git commit -m "refactor: separate ORM models from specialized Pydantic DTOs"
```

---

### Task 3: Background Tasks with arq

**Files:**
- Create: `backend/app/core/worker.py`
- Modify: `backend/app/jobs.py` (will be merged into worker or replaced)
- Modify: `backend/app/tasks.py` (rename or refactor)

- [ ] **Step 1: Configure arq Worker**
Define `WorkerSettings` in `backend/app/core/worker.py`. Register background functions (agent tasks, recommendation jobs).

- [ ] **Step 2: Refactor Task Dispatching**
Replace `rq` Queue logic with `arq` pool dispatching in routers and scorers.

- [ ] **Step 3: Commit**
```bash
git add backend/app/core/worker.py backend/app/jobs.py
git commit -m "feat: migrate background tasks from rq to arq"
```

---

### Task 4: API Routers Refactor

**Files:**
- Create: `backend/app/api/v1/auth.py`
- Create: `backend/app/api/v1/recommendations.py`
- Create: `backend/app/api/v1/parser.py`
- Create: `backend/app/api/deps.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Move Dependencies**
Move `get_db`, `get_current_user`, and `get_current_active_user` to `backend/app/api/deps.py`. Add arq pool dependency.

- [ ] **Step 2: Create Auth Router**
Move register/token endpoints from `main.py` to `api/v1/auth.py`.

- [ ] **Step 3: Create Recommendations Router**
Move recommend/enqueue/job-status endpoints to `api/v1/recommendations.py`.

- [ ] **Step 4: Create Parser Router**
Move transcript parsing endpoint to `api/v1/parser.py`.

- [ ] **Step 5: Clean up `main.py`**
Include routers in `main.py`. Handle arq pool lifecycle (startup/shutdown).

- [ ] **Step 6: Commit**
```bash
git add backend/app/api/ backend/app/main.py
git commit -m "refactor: restructure into modular routers and dependencies"
```

---

### Task 5: Final Cleanup and Integration

**Files:**
- Remove: `backend/app/auth.py`
- Modify: `backend/app/scoring/*.py`
- Modify: `backend/app/db.py`
- Modify: `backend/requirements.txt`
- Modify: `docker-compose.yml`

- [ ] **Step 1: Update imports across the codebase**
Ensure all scoring components use the new paths for models, schemas, and config. Update `RAGScorer` to use `arq`.

- [ ] **Step 2: Clean up db.py**
Keep `db.py` focused on engine/session creation. Move helper functions (`get_all_courses`, etc.) to a new `backend/app/crud.py`.

- [ ] **Step 3: Update Requirements and Docker**
Replace `rq` with `arq` in `requirements.txt`. Update `docker-compose.yml` worker command.

- [ ] **Step 4: Verification**
Run all tests to ensure the refactor didn't break functionality.

- [ ] **Step 5: Commit**
```bash
git rm backend/app/auth.py
git commit -m "cleanup: remove legacy files and finalize arq integration"
```
