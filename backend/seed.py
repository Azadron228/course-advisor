from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infrastructure.db.models import UserORM
from app.core.config import settings
from app.core.security import get_password_hash


def seed():
    print("Starting database seeding...")
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Seed Admin User
    print("Seeding admin user...")
    admin_email = "admin@example.com"
    admin_user = session.query(UserORM).filter(UserORM.email == admin_email).first()
    if not admin_user:
        admin_user = UserORM(
            email=admin_email,
            hashed_password=get_password_hash("admin"),
            full_name="System Administrator",
            is_admin=True,
        )
        session.add(admin_user)
    else:
        admin_user.is_admin = True

    session.commit()
    session.close()
    print("Seeding complete.")


if __name__ == "__main__":
    seed()
