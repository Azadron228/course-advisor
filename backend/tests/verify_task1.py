from backend.app.core.config import settings
from backend.app.core.security import get_password_hash, verify_password, create_access_token


def verify_task1():
    print("Verifying Settings...")
    print(f"PROJECT_NAME: {settings.PROJECT_NAME}")
    print(f"ALGORITHM: {settings.ALGORITHM}")
    print(f"DATABASE_URL: {settings.DATABASE_URL}")

    print("\nVerifying Security Helpers...")
    password = "test_password"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)
    print("Password hashing/verification: OK")

    token = create_access_token(data={"sub": "test@example.com"})
    assert isinstance(token, str)
    print(f"JWT token generation: OK")

    print("\nTask 1 Verification: SUCCESS")


if __name__ == "__main__":
    verify_task1()
