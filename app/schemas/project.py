from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
import enum


class ProjectRole(str, enum.Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"


# --- PROJECT SCHEMAS ---
# Schema ProjectBase: Chứa các trường thông tin chung của dự án


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=5, max_length=50,
                      description="Tên dự án không được để trống và tối đa 50 ký tự")
    description: Optional[str] = Field(
        None, max_length=1000, description="Mô tả dự án tối đa 1000 ký tự")

class ProjectCreate(ProjectBase):
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str):
        if not v.strip():
            raise ValueError("Tên dự án không được chỉ chứa khoảng trắng")
        if len(v.strip()) < 5:
            raise ValueError("Tên dự án phải chứa ít nhất 5 ký tự hợp lệ")
        return v.strip()


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=5, max_length=50,
                                description="Tên dự án không được để trống và tối đa 50 ký tự")
    description: Optional[str] = Field(
        None, max_length=1000, description="Mô tả dự án tối đa 1000 ký tự")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]):
        if v is not None:
            if not v.strip():
                raise ValueError("Tên dự án không được chỉ chứa khoảng trắng")
            if len(v.strip()) < 5:
                raise ValueError("Tên dự án phải chứa ít nhất 5 ký tự hợp lệ")
            return v.strip()
        return v

# Schema ProjectResponse: Schema dùng để format output khi trả chi tiết dự án về client


class ProjectResponse(ProjectBase):
    id: int = Field(..., description="ID của dự án")
    owner_id: int = Field(..., description="ID của chủ sở hữu dự án")
    created_at: datetime = Field(..., description="Thời gian tạo dự án")

    members: "list[ProjectMemberResponse]" = Field(
        ..., description="Danh sách thành viên")
    model_config = ConfigDict(from_attributes=True)

# --- PROJECT MEMBER SCHEMAS ---


class ProjectMemberBase(BaseModel):
    user_id: int = Field(..., description="ID của người dùng")
    role: ProjectRole = Field(
        ProjectRole.MEMBER, description="Vai trò của người dùng trong dự án")


class ProjectMemberCreate(ProjectMemberBase):
    pass


class ProjectMemberUpdate(BaseModel):
    role: Optional[ProjectRole] = Field(
        None, description="Vai trò của người dùng trong dự án")

# Schema ProjectMemberResponse: Schema hiển thị thông tin member trong dự án


class ProjectMemberResponse(ProjectMemberBase):
    project_id: int = Field(..., description="ID của dự án")
    joined_at: datetime = Field(..., description="Thời gian tham gia dự án")

    model_config = ConfigDict(from_attributes=True)


ProjectResponse.model_rebuild()
