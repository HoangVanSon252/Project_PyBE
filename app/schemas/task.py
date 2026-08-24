from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
import enum


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, description="Nội dung bình luận")


class CommentResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    content: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AttachmentResponse(BaseModel):
    id: int
    task_id: int
    uploader_id: int
    file_name: str
    file_url: str
    file_type: Optional[str]
    file_size: Optional[int]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TaskStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

class TaskPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Tiêu đề công việc không được để trống và tối đa 255 ký tự")
    description: Optional[str] = Field(None, max_length=1000, description="Mô tả công việc tối đa 1000 ký tự")
    status: TaskStatus = Field(TaskStatus.TODO, description="Trạng thái công việc")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Độ ưu tiên công việc")
    due_date: Optional[datetime] = Field(None, description="Ngày hết hạn công việc")

class TaskCreate(TaskBase):
    assignee_id: Optional[int] = Field(None, description="ID của người được giao")

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Tiêu đề công việc không được để trống và tối đa 255 ký tự")
    description: Optional[str] = Field(None, max_length=1000, description="Mô tả công việc tối đa 1000 ký tự")
    assignee_id: Optional[int] = Field(None, description="ID của người được giao")
    status: Optional[TaskStatus] = Field(None, description="Trạng thái công việc")
    priority: Optional[TaskPriority] = Field(None, description="Độ ưu tiên công việc")
    due_date: Optional[datetime] = Field(None, description="Ngày hết hạn công việc")

class TaskResponse(TaskBase):
    id: int = Field(..., description="ID của công việc")
    project_id: int = Field(..., description="ID của dự án")
    assignee_id: Optional[int] = Field(None, description="ID của người được giao")
    creator_id: int = Field(..., description="ID của người tạo công việc")
    comments: list[CommentResponse] = Field(..., description="Danh sách bình luận")
    attachments: list[AttachmentResponse] = Field(..., description="Danh sách file đính kèm")
    created_at: datetime = Field(..., description="Thời gian tạo công việc")
    
    model_config = ConfigDict(from_attributes=True)
