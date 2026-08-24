from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
import enum

class ProjectRole(str, enum.Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"

# --- PROJECT SCHEMAS ---
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Tên dự án không được để trống và tối đa 255 ký tự")
    description: Optional[str] = Field(None, max_length=1000, description="Mô tả dự án tối đa 1000 ký tự")

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Tên dự án không được để trống và tối đa 255 ký tự")
    description: Optional[str] = Field(None, max_length=1000, description="Mô tả dự án tối đa 1000 ký tự")

class ProjectResponse(ProjectBase):
    id: int = Field(..., description="ID của dự án")
    owner_id: int = Field(..., description="ID của chủ sở hữu dự án")
    created_at: datetime = Field(..., description="Thời gian tạo dự án")
    
    members: list[ProjectMemberResponse] = Field(..., description="Danh sách thành viên")
    model_config = ConfigDict(from_attributes=True)

# --- PROJECT MEMBER SCHEMAS ---
class ProjectMemberBase(BaseModel):
    user_id: int = Field(..., description="ID của người dùng")
    role: ProjectRole = Field(ProjectRole.MEMBER, description="Vai trò của người dùng trong dự án")

class ProjectMemberCreate(ProjectMemberBase):
    pass

class ProjectMemberUpdate(BaseModel):
    role: Optional[ProjectRole] = Field(None, description="Vai trò của người dùng trong dự án")

class ProjectMemberResponse(ProjectMemberBase):
    project_id: int = Field(..., description="ID của dự án")
    joined_at: datetime = Field(..., description="Thời gian tham gia dự án")
    
    model_config = ConfigDict(from_attributes=True)
