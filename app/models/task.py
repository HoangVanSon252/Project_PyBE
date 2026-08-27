import enum
from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.database import Base
from sqlalchemy.orm import relationship

# Enum trạng thái của công việc (TODO, IN_PROGRESS, DONE)
class TaskStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

# Enum mức độ ưu tiên của công việc
class TaskPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

# Bảng Tasks: Lưu thông tin chi tiết các công việc thuộc về dự án
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(TaskStatus), nullable=False, default= TaskStatus.TODO)
    priority = Column(Enum(TaskPriority), nullable=False, default= TaskPriority.MEDIUM)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


    # Các mối quan hệ (Relationships)
    # Công việc thuộc về 1 Dự án (n-1)
    project = relationship("Project", back_populates="tasks")
    # Công việc được giao cho 1 Người dùng (n-1)
    assignee = relationship("Users", foreign_keys=[assignee_id], back_populates="tasks")
    # Công việc được tạo bởi 1 Người dùng (n-1)
    creator = relationship("Users", foreign_keys=[creator_id])

    # Công việc có nhiều bình luận (1-n)
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")
    # Công việc có nhiều file đính kèm (1-n)
    attachments = relationship("TaskAttachment", back_populates="task", cascade="all, delete-orphan")
