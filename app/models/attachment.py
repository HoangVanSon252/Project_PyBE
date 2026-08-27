from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.database import Base
from sqlalchemy.orm import relationship

# Bảng TaskAttachment: Lưu thông tin các tệp đính kèm của công việc
class TaskAttachment(Base):
    __tablename__ = "task_attachments"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    file_name = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=True)
    file_size = Column(Integer, nullable=True)   
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Các mối quan hệ (Relationships)
    # File đính kèm thuộc về 1 Công việc (n-1)
    task = relationship("Task", back_populates="attachments")
    # File đính kèm do 1 Người dùng upload (n-1)
    uploader = relationship("Users")