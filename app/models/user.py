from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum

# Định nghĩa các vai trò của người dùng trên hệ thống
class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    MANAGER = "MANAGER"

# Bảng Users: Lưu thông tin tài khoản người dùng
class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Các mối quan hệ (Relationships)
    # 1 User có thể tạo/sở hữu nhiều Dự án (1-n)
    owner_project = relationship('Project', back_populates='owner')
    # 1 User có thể tham gia nhiều Dự án với tư cách thành viên (1-n với bảng trung gian ProjectMember)
    project_members = relationship("ProjectMember", back_populates="user")
    # 1 User có thể được giao nhiều Công việc (1-n)
    tasks = relationship("Task", back_populates="assignee", foreign_keys="[Task.assignee_id]")
    # 1 User có thể tạo nhiều Công việc (1-n)
    created_tasks = relationship("Task", back_populates="creator", foreign_keys="[Task.creator_id]")