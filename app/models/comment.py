from app.db.database import Base
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


# Bảng TaskComment: Lưu trữ các bình luận của người dùng trên một công việc
class TaskComment(Base):
    __tablename__ = "task_comment"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Các mối quan hệ (Relationships)
    # Bình luận thuộc về 1 Công việc (n-1)
    task = relationship("Task", back_populates="comments")
    # Bình luận do 1 Người dùng viết (n-1)
    user = relationship("Users", foreign_keys=[user_id])