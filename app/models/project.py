from sqlalchemy.orm import relationship
import enum
from sqlalchemy.sql import func
from app.db.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum, Boolean

# Enum vai trò của thành viên trong dự án


class ProjectRole(str, enum.Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"

# Bảng Projects: Lưu thông tin các dự án


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_deleted = Column(Boolean, default=False)
    delete_at = Column(DateTime(timezone=True), nullable=True)

    # Các mối quan hệ (Relationships)
    # Dự án thuộc về 1 Chủ sở hữu (n-1 với Users)
    owner = relationship("Users", back_populates="owner_project")
    # Dự án có nhiều thành viên (1-n với bảng trung gian ProjectMember)
    members = relationship(
        "ProjectMember", back_populates="project", cascade="all, delete-orphan")
    # Dự án có nhiều công việc (1-n với bảng Tasks)
    tasks = relationship("Task", back_populates="project",
                         cascade="all, delete-orphan")


# Bảng ProjectMember: Lưu quan hệ n-n giữa Người dùng và Dự án (gồm Role)
class ProjectMember(Base):
    __tablename__ = "project_members"
    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role = Column(Enum(ProjectRole), nullable=False,
                  default=ProjectRole.VIEWER)
    joined_at = Column(DateTime(timezone=True),
                       server_default=func.now(), nullable=False)

    # Các mối quan hệ (Relationships)
    # Liên kết tới Dự án (n-1)
    project = relationship("Project", back_populates="members")
    # Liên kết tới Người dùng (n-1)
    user = relationship("Users", back_populates="project_members")
