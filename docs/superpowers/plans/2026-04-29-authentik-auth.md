# authentik OIDC Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace local authentication with authentik OIDC SSO while maintaining local user profiles.

**Architecture:** Frontend redirects to authentik for login. Backend verifies authentik-issued JWTs using JWKS and syncs user data into the local `users` table on each authenticated request.

**Tech Stack:** FastAPI, Next.js, PyJWT (or Authlib), SQLAlchemy.

---

### Task 1: Backend Configuration

**Files:**
- Modify: `backend/app/core/config.py`

- [ ] **Step 1: Add authentik settings to `Settings` class**

```python
    # authentik
    AUTHENTIK_URL: Optional[str] = None
    AUTHENTIK_CLIENT_ID: Optional[str] = None
    AUTHENTIK_CLIENT_SECRET: Optional[str] = None
    
    @property
    def AUTHENTIK_OPENID_CONFIG_URL(self) -> str:
        if not self.AUTHENTIK_URL:
            return ""
        return f"{self.AUTHENTIK_URL}/application/o/course-advisor/.well-known/openid-configuration"
```

- [ ] **Step 2: Commit changes**

```bash
git add backend/app/core/config.py
git commit -m "feat(auth): add authentik settings to config"
```

### Task 2: Database Migration for Nullable Passwords

**Files:**
- Modify: `backend/app/infrastructure/db/models.py`
- Create: `backend/alembic/versions/xxxx_make_password_nullable.py` (via `alembic revision`)

- [ ] **Step 1: Update `UserORM` to make `hashed_password` optional**

```python
class UserORM(Base):
    __tablename__ = "users"
    # ...
    hashed_password: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    # ...
```

- [ ] **Step 2: Generate and run migration**

```bash
cd backend
alembic revision --autogenerate -m "make_password_nullable"
alembic upgrade head
```

- [ ] **Step 3: Commit changes**

```bash
git add backend/app/infrastructure/db/models.py backend/alembic/versions/
git commit -m "db: make hashed_password nullable for OIDC users"
```

### Task 3: Security Logic (OIDC Verification)

**Files:**
- Modify: `backend/app/core/security.py`

- [ ] **Step 1: Implement `verify_authentik_token`**

```python
import httpx
import jwt
from jwt import PyJWKClient

def verify_authentik_token(token: str) -> dict:
    if not settings.AUTHENTIK_URL:
        # Fallback to local validation for dev or raise error
        raise HTTPException(status_code=500, detail="authentik not configured")
        
    url = f"{settings.AUTHENTIK_URL}/application/o/course-advisor/jwks/"
    jwks_client = PyJWKClient(url)
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    
    data = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=settings.AUTHENTIK_CLIENT_ID,
        issuer=f"{settings.AUTHENTIK_URL}/application/o/course-advisor/"
    )
    return data
```

- [ ] **Step 2: Commit changes**

```bash
git add backend/app/core/security.py
git commit -m "feat(auth): implement authentik token verification"
```

### Task 4: Dependency Refactoring & User Sync

**Files:**
- Modify: `backend/app/api/deps.py`

- [ ] **Step 1: Update `get_current_user` to use OIDC and sync users**

```python
async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        # Verify token via authentik
        payload = verify_authentik_token(token)
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=401, detail="Token missing email")
    except Exception as e:
        # Fallback for existing local tokens during transition if needed
        # Or just raise 401
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    user_repo = UserRepository(db)
    user = user_repo.get_by_email(email)
    
    if user is None:
        # Sync User (Shadow User creation)
        new_user = User(
            id=None,
            email=email,
            full_name=payload.get("name"),
            is_active=True,
            onboarding_completed=False
        )
        user = user_repo.create(new_user)
        
    return user
```

- [ ] **Step 2: Commit changes**

```bash
git add backend/app/api/deps.py
git commit -m "feat(auth): sync authentik users to local database"
```

### Task 5: Frontend OIDC Logic

**Files:**
- Modify: `frontend/src/hooks/use-auth.ts`

- [ ] **Step 1: Update `login` to redirect to authentik**

```typescript
  const login = async () => {
    const authUrl = `${process.env.NEXT_PUBLIC_AUTHENTIK_URL}/application/o/authorize/`;
    const clientId = process.env.NEXT_PUBLIC_AUTHENTIK_CLIENT_ID;
    const redirectUri = `${window.location.origin}/auth/callback`;
    const scope = 'openid profile email';
    const responseType = 'token'; // Or 'code' for Auth Code flow
    
    const url = `${authUrl}?client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}&scope=${encodeURIComponent(scope)}&response_type=${responseType}`;
    window.location.href = url;
  };
```

- [ ] **Step 2: Commit changes**

```bash
git add frontend/src/hooks/use-auth.ts
git commit -m "feat(auth): update login to use OIDC redirect"
```

### Task 6: Login UI Update

**Files:**
- Modify: `frontend/src/app/[locale]/login/page.tsx`

- [ ] **Step 1: Replace login form with "Login with authentik" button**

- [ ] **Step 2: Commit changes**

```bash
git add frontend/src/app/[locale]/login/page.tsx
git commit -m "ui(auth): replace login form with authentik SSO button"
```

### Task 7: OIDC Callback Handler

**Files:**
- Create: `frontend/src/app/[locale]/auth/callback/page.tsx`

- [ ] **Step 1: Implement callback page to capture token and redirect**

- [ ] **Step 2: Commit changes**

```bash
git add frontend/src/app/[locale]/auth/callback/page.tsx
git commit -m "feat(auth): add OIDC callback handler"
```
