# Task 1: Project Scaffolding & Docker Setup - Completion Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the scaffolding by adding frontend requirements and ensuring the Docker environment builds successfully.

**Architecture:** A multi-container Docker setup with services for database (PostgreSQL/pgvector), backend (FastAPI), and frontend (Streamlit).

**Tech Stack:** Docker, Docker Compose, Python, FastAPI, Streamlit.

---

### Task 1.1: Create frontend/requirements.txt

**Files:**
- Create: `frontend/requirements.txt`

- [ ] **Step 1: Write the failing test**

Add a test case to `tests/test_scaffolding.py` (if not already there) to check for the content of `frontend/requirements.txt`.
Wait, the test `test_frontend_requirements_exists` already exists and fails. I'll add a check for the content.

```python
    def test_frontend_requirements_content(self):
        requirements_path = 'frontend/requirements.txt'
        self.assertTrue(os.path.exists(requirements_path))
        with open(requirements_path, 'r') as f:
            content = f.read()
        self.assertIn('streamlit', content)
        self.assertIn('httpx', content)
        self.assertIn('pandas', content)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_scaffolding.py`
Expected: FAIL

- [ ] **Step 3: Create frontend directory and requirements.txt**

```bash
mkdir -p frontend
cat <<EOF > frontend/requirements.txt
streamlit
httpx
pandas
EOF
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_scaffolding.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/requirements.txt
git commit -m "feat: add frontend requirements"
```

---

### Task 1.2: Add Dockerfiles and Verify Docker Setup

**Files:**
- Create: `backend/Dockerfile`
- Create: `frontend/Dockerfile`

- [ ] **Step 1: Create backend/Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: Create frontend/Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

- [ ] **Step 3: Create placeholder main.py and app.py to satisfy Docker builds (if needed)**

```bash
touch backend/main.py
touch frontend/app.py
```

- [ ] **Step 4: Run docker-compose build**

Run: `docker-compose build`
Expected: Successful build of all services (db, backend, frontend).

- [ ] **Step 5: Commit**

```bash
git add backend/Dockerfile frontend/Dockerfile backend/main.py frontend/app.py
git commit -m "feat: add Dockerfiles and verify docker-compose build"
```
