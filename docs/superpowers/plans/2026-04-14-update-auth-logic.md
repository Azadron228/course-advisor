# Update Authentication Logic Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor authentication logic in `backend/app/auth.py` to use SQLAlchemy sessions and email-based identification.

**Architecture:** Update auth functions to accept a `Session` object and query users by email instead of email. Update JWT token data to use email as the subject.

**Tech Stack:** FastAPI, SQLAlchemy, PyJWT, Argon2 (via pwdlib).

---

### Task 1: Research and Setup Reproduction

**Files:**
- Create: `tests/repro_task4.py`

- [ ] **Step 1: Create a reproduction script to demonstrate current breakage**

```python
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.auth import authenticate_user
from sqlalchemy.orm import Session
from app.db import SessionLocal, Base, engine

# Setup test DB
Base.metadata.create_all(bind=engine)

def test_repro_current_breakage():
    db = SessionLocal()
    try:
        # This should fail because authenticate_user currently doesn't accept 'db'
        # and it calls get_user_by_email which is missing from db.py
        authenticate_user(db, "test@example.com", "password")
    except TypeError as e:
        print(f"Caught expected TypeError: {e}")
    except ImportError as e:
        print(f"Caught expected ImportError: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_repro_current_breakage()
```

- [ ] **Step 2: Run reproduction script**

Run: `python3 tests/repro_task4.py`
Expected: FAIL (likely with ImportError or TypeError)

- [ ] **Step 3: Commit reproduction script**

```bash
git add tests/repro_task4.py
git commit -m "test: add reproduction script for Task 4"
```

### Task 2: Update `backend/app/auth.py` Imports and Functions

**Files:**
- Modify: `backend/app/auth.py`

- [ ] **Step 1: Update imports to use `get_user_by_email` and `get_db`**

```python
from .db import get_user_by_email, get_db
from sqlalchemy.orm import Session
```

- [ ] **Step 2: Update `authenticate_user` to use `Session` and `email`**

```python
def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
```

- [ ] **Step 3: Update `get_current_user` to use `Session` and `email`**

```python
async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user_by_email(db, token_data.email)
    if user is None:
        raise credentials_exception
    return user
```

- [ ] **Step 4: Update `get_current_active_user` as needed**

```python
async def get_current_active_user(current_user: UserORM = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
```
(Note: Using `UserORM` instead of `UserInDB` where appropriate)

- [ ] **Step 5: Run tests to verify fix**

Update `tests/repro_task4.py` to use the new API and run it.

- [ ] **Step 6: Commit changes**

```bash
git add backend/app/auth.py
git commit -m "refactor: update auth logic to use email and SQLAlchemy"
```

### Task 3: Verification and Cleanup

**Files:**
- Modify: `tests/test_auth.py` (Create if doesn't exist)
- Delete: `tests/repro_task4.py`

- [ ] **Step 1: Create comprehensive auth tests**

- [ ] **Step 2: Run all tests**

- [ ] **Step 3: Cleanup reproduction script**

```bash
rm tests/repro_task4.py
git add tests/test_auth.py
git commit -m "test: add comprehensive auth tests"
```
