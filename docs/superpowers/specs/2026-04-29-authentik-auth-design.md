# Design Spec: authentik OIDC Integration

## 1. Goal
Replace the current local JWT-based authentication with **authentik** using the OpenID Connect (OIDC) protocol. This will provide Single Sign-On (SSO) capabilities while maintaining application-specific user data in a local database.

## 2. Approach: OIDC with Local Shadow Users
We will use authentik as the external Identity Provider (IdP). The application will act as an OIDC Client.

- **Frontend**: Handles the redirect flow to authentik for login.
- **Backend**: Validates tokens issued by authentik and syncs user profiles into the local database.

## 3. Architecture & Components

### 3.1 Backend (FastAPI)
- **Configuration**:
    - `AUTHENTIK_URL`: Base URL of the authentik server.
    - `AUTHENTIK_CLIENT_ID`: OAuth2 Client ID.
    - `AUTHENTIK_CLIENT_SECRET`: OAuth2 Client Secret.
    - `AUTHENTIK_OPENID_CONFIG_URL`: `f"{AUTHENTIK_URL}/application/o/course-advisor/.well-known/openid-configuration"`
- **Security Logic (`app/core/security.py`)**:
    - Implement a `verify_token` function that uses `PyJWT` or `Authlib` to:
        1. Fetch the OpenID configuration and JWKS from authentik.
        2. Verify the token signature, audience, and expiration.
- **Dependency (`app/api/deps.py`)**:
    - Update `get_current_user` to:
        1. Extract the bearer token.
        2. Validate it via the new security logic.
        3. Extract `email`, `sub`, and `name` from the token claims.
        4. Upsert a local `User` record in the database using the email as the identifier.
- **API Routes**:
    - Deprecate `/api/v1/auth/token` (login) and `/api/v1/auth/register`.
    - Retain `/api/v1/auth/me` for fetching the synced user profile.

### 3.2 Frontend (Next.js)
- **Environment**:
    - `NEXT_PUBLIC_AUTHENTIK_URL`: Public URL of the authentik server.
    - `NEXT_PUBLIC_AUTHENTIK_CLIENT_ID`: Public Client ID.
- **Auth Hook (`src/hooks/use-auth.ts`)**:
    - Update `login` to redirect the browser to authentik's authorization endpoint.
    - Implement a `handleCallback` function (or a dedicated route) to exchange the code for a token (if using Authorization Code flow) or just capture the token (if using Implicit flow, though Auth Code + PKCE is preferred).
- **UI**:
    - Update the login page to remove the email/password form and add a "Login with authentik" button.

### 3.3 Database
- **Migration**:
    - Update the `users` table: make `hashed_password` nullable.

## 4. Implementation Plan (High-Level)
1. **Branch Creation**: Create `feat/authentik-auth` branch.
2. **Backend Refactor**:
    - Update `Settings` in `config.py`.
    - Implement token validation in `security.py`.
    - Update `get_current_user` in `deps.py`.
    - Create a database migration to make `hashed_password` nullable.
3. **Frontend Refactor**:
    - Update `useAuth` hook.
    - Update Login page.
    - Handle the OIDC callback.
4. **Verification**:
    - Test the full login flow against a local or development authentik instance.
    - Verify that local user data (career goals, etc.) is correctly linked to authentik users.

## 5. Success Criteria
- Users can log in via authentik.
- Local database contains shadow records for all logged-in users.
- Application-specific features (learning plans, etc.) work correctly for authenticated users.
- Legacy password-based login is disabled.
