from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime
import enum


class RoleEnum(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Email của người dùng")
    password: str = Field(..., description="Mật khẩu của người dùng")



class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Email của người dùng")
    full_name: str = Field(..., description="Họ tên đầy đủ của người dùng")

class UserCreate(UserBase):
    password: str = Field(..., description="Mật khẩu của người dùng")

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, description="Email của người dùng")
    full_name: Optional[str] = Field(None, description="Họ tên đầy đủ của người dùng")
    password: Optional[str] = Field(None, description="Mật khẩu của người dùng")
    role: Optional[RoleEnum] = Field(None, description="Vai trò của người dùng")
    is_active: Optional[bool] = Field(None, description="Trạng thái hoạt động của người dùng")

class UserResponse(UserBase):
    id: int = Field(..., description="ID của người dùng")
    role: RoleEnum = Field(..., description="Vai trò của người dùng")
    is_active: bool = Field(..., description="Trạng thái hoạt động của người dùng")
    created_at: datetime = Field(..., description="Thời gian tạo người dùng")
    
    model_config = ConfigDict(from_attributes=True)
