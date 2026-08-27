from fastapi import APIRouter, status, Depends, Query
from app.schemas.response import ResponseSchemas
from app.schemas.user import UserResponse
from app.dependencies.deps import get_current_user, get_current_user_is_admin
from sqlalchemy.orm import Session
from typing import Optional
from app.dependencies.deps import get_db
from app.models.user import Users
from app.models.user import UserRole
from datetime import datetime

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get(
    "/me",
    response_model=ResponseSchemas[UserResponse],
    summary="Thông tin cá nhân",
    description="Lấy thông tin của người dùng đang đăng nhập dựa trên token. Không trả về password_hash."
)
# API Lấy thông tin cá nhân của User hiện tại (Profile)
async def get_user(current_user: Users = Depends(get_current_user)):
    return ResponseSchemas(
        success=True,
        message="Lấy thông tin người dùng thành công",
        data={
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "role": current_user.role,
            "is_active": current_user.is_active,
            "created_at": current_user.created_at,
            "account_age_days": (datetime.now() - current_user.created_at).days
        }
    )

@router.get(
    "",
    response_model=ResponseSchemas[list[UserResponse]],
    summary="Danh sách người dùng (Chỉ Admin)",
    description="Lấy danh sách tất cả người dùng trong hệ thống. Chỉ tài khoản có role ADMIN mới được phép truy cập."
) 
# API Lấy danh sách toàn bộ User (Chỉ Admin mới có quyền truy cập, hỗ trợ tìm kiếm và lọc trạng thái)
async def get_list_user(
    search: Optional[str] = Query(None, description="Tìm kiếm theo Tên hoặc Email"),
    is_active: Optional[bool] = Query(None, description="Lọc theo trạng thái hoạt động"),
    db: Session = Depends(get_db),
    admin_user: Users = Depends(get_current_user_is_admin)
):  
    query_users = db.query(Users)

    if search:
        query_users = query_users.filter(
            Users.full_name.ilike(f"%{search}%") |
            Users.email.ilike(f"%{search}%")
        )
    if is_active is not None:
        query_users = query_users.filter(Users.is_active == is_active)
    users = query_users.all()
    return ResponseSchemas(
        success=True,
        message="Lấy danh sách người dùng thành công",
        data=users
    )
