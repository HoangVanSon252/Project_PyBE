from sqlalchemy import create_engine
from app.core.config import settings
from sqlalchemy.orm import sessionmaker, declarative_base
# Khởi tạo Engine kết nối đến MySQL thông qua SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    pool_recycle=3600,
    pool_pre_ping=True
)
# Tạo một SessionLocal class dùng để sinh ra các DB Session phục vụ query
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

# Khởi tạo Base class để các model ORM khác kế thừa
Base = declarative_base()
