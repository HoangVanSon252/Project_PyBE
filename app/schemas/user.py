from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator, model_validator
from datetime import datetime
import enum


# Enum role người dùng (USER, ADMIN)
class RoleEnum(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"


# Schema LoginRequest: Validate payload khi đăng nhập
class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Email của người dùng")
    password: str = Field(..., description="Mật khẩu của người dùng",)


# Schema UserBase: Các trường thông tin cơ bản của User
class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Email của người dùng")
    full_name: str = Field(..., min_length=5, max_length=255,
                           description="Họ tên đầy đủ của người dùng")


# Schema UserCreate: Kế thừa UserBase
class UserCreate(UserBase):
    password: str = Field(..., min_length=8,  max_length=20,
                          description="Mật khẩu của người dùng")
    confirm_password : str = Field(..., min_length=8,  max_length=20)

    @field_validator("full_name")
    @classmethod
    def normalize_name(cls, value: str):
        value = " ".join(value.split())
        if any(ord(char) < 32 for char in value):
            raise ValueError("Họ tên chứa ký tự không hợp lệ")
        return value

    @model_validator(mode="after")
    def validate_password_confirmation(self):
        if self.password != self.confirm_password:
            raise ValueError("Mật khẩu xác nhận không khớp")
        return self


# Schema UserUpdate: Dùng khi cần cập nhật tài khoản
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, description="Email của người dùng")
    full_name: Optional[str] = Field(
        None, description="Họ tên đầy đủ của người dùng")
    password: Optional[str] = Field(
        None, description="Mật khẩu của người dùng")
    role: Optional[RoleEnum] = Field(
        None, description="Vai trò của người dùng")
    is_active: Optional[bool] = Field(
        None, description="Trạng thái hoạt động của người dùng")


# Schema UserResponse: Định dạng dữ liệu trả về cho client sau khi query từ DB
class UserResponse(UserBase):
    id: int = Field(..., description="ID của người dùng")
    role: RoleEnum = Field(..., description="Vai trò của người dùng")
    is_active: bool = Field(...,
                            description="Trạng thái hoạt động của người dùng")
    created_at: datetime = Field(..., description="Thời gian tạo người dùng")
    model_config = ConfigDict(from_attributes=True)


class UserRegisterResponse(BaseModel):
    id: int = Field(..., description="ID của người dùng")
    email: EmailStr = Field(..., description="Email của người dùng")

    model_config = ConfigDict(from_attributes=True)


class UserIsAdmin(UserResponse):
    is_admin: bool
    model_config = ConfigDict(from_attributes=True)
