from fastapi import APIRouter, status, Depends, Query
from app.schemas.response import ResponseSchemas
from app.schemas.user import UserResponse
from app.dependencies.deps import get_current_user, get_current_user_is_admin
from sqlalchemy.orm import Session
from typing import Optional
from app.dependencies.deps import get_db
from app.models.user import Users
from app.models.user import UserRole

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/me", response_model = ResponseSchemas[UserResponse])
def get_user(current_user: UserResponse = Depends(get_current_user)):
    return ResponseSchemas(
        success=True,
        message="Lấy thông tin người dùng thành công",
        data=current_user
    )

@router.get("", response_model = ResponseSchemas[list[UserResponse]])
def get_list_user(
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
