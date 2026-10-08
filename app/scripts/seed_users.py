"""Create development users for each application role, idempotently."""
import os
import sys
from pathlib import Path

# Allows `python -m scripts.seed_users` when the current directory is app/.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.db.database import SessionLocal
from app.models.user import Users, UserRole
from app.core.security import get_hashed_password

SEED_USERS = [
    ("admin@example.com", "Admin User", UserRole.ADMIN, "SEED_ADMIN_PASSWORD"),
    ("manager@example.com", "Manager User", UserRole.MANAGER, "SEED_MANAGER_PASSWORD"),
    ("user@example.com", "Regular User", UserRole.USER, "SEED_USER_PASSWORD"),
]

def main():
    db = SessionLocal()
    try:
        for email, name, role, env_name in SEED_USERS:
            password = os.getenv(env_name, "ChangeMe123!")
            user = db.query(Users).filter(Users.email == email).first()
            if user:
                user.role, user.is_active = role, True
            else:
                db.add(Users(email=email, full_name=name, role=role, is_active=True, password_hash=get_hashed_password(password)))
        db.commit()
        print("Seeded admin@example.com, manager@example.com and user@example.com")
        if os.getenv("ENVIRONMENT", "development") == "production":
            print("WARNING: set SEED_*_PASSWORD explicitly before production seeding")
    finally:
        db.close()

if __name__ == "__main__":
    main()
