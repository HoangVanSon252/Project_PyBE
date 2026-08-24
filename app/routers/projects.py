from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.dependencies.deps import get_db, get_current_user
from app.services.project import project_service
from app.schemas.project import ProjectCreate,ProjectResponse,ProjectUpdate, ProjectMemberResponse, ProjectMemberCreate
from app.schemas.response import ResponseSchemas
from app.models.user import Users
from typing import Optional

router = APIRouter(
    prefix="/projects",
    tags=["projects"]
)


@router.post("/", response_model=ResponseSchemas[ProjectResponse])
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    new_project = project_service.create_project(db, project, current_user.id)
    return ResponseSchemas(
        success=True,
        message="Tạo dự án thành công",
        data=new_project
    )

@router.get("/", response_model=ResponseSchemas[list[ProjectResponse]])
async def get_list_project(
    search: Optional[str] = Query(None, description="Tìm kiếm theo tên dự án"),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    list_project = project_service.get_list_project(db, current_user.id, search)
    return ResponseSchemas(
        success=True,
        message="Lấy danh sách dự án thành công",
        data=list_project
    )

@router.get("/{project_id}", response_model=ResponseSchemas[ProjectResponse])
async def get_project_by_id(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    project = project_service.get_project_by_id(db, project_id, current_user.id)
    return ResponseSchemas(
        success=True,
        message="Lấy thông tin dự án thành công",
        data=project
    )

@router.put("/{project_id}", response_model=ResponseSchemas[ProjectResponse])
async def update_project(
    project: ProjectUpdate,
    project_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    updated_project = project_service.update_project(db, project, project_id, current_user.id)
    return ResponseSchemas(
        success=True,
        message="Cập nhật dự án thành công",
        data=updated_project
    )

@router.delete("/{project_id}", response_model=ResponseSchemas[ProjectResponse])
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    deleted_project = project_service.delete_project(db, project_id, current_user.id)
    return ResponseSchemas(
        success=True,
        message="Xóa dự án thành công",
        data=deleted_project
    )

@router.post("/{project_id}/members", response_model=ResponseSchemas[ProjectMemberResponse])
async def add_member_to_project(
    project_id: int,
    member: ProjectMemberCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    new_member = project_service.add_member_to_project(db, project_id, current_user.id, member)
    return ResponseSchemas(
        success=True,
        message="Thêm thành viên vào dự án thành công",
        data=new_member
    )

@router.get("/{project_id}/members", response_model=ResponseSchemas[list[ProjectMemberResponse]])
async def get_members_from_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    members = project_service.get_member_project(db, project_id, current_user.id)
    return ResponseSchemas(
        success=True,
        message="Lấy danh sách thành viên thành công",
        data=members
    )

@router.delete("/{project_id}/members/{member_id}", response_model=ResponseSchemas[ProjectMemberResponse])
async def remove_member_from_project(
    project_id: int,
    member_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    removed_member = project_service.delete_member_project(db, project_id, current_user.id, member_id)
    return ResponseSchemas(
        success=True,
        message="Xóa thành viên khỏi dự án thành công",
        data=removed_member
    )
