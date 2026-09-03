from sqlalchemy.orm import Session
from app.models.activity import ActivityLogModel
from app.models.project import Project, ProjectMember, ProjectRole
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectMemberCreate, ProjectMemberUpdate
from app.models.user import Users
from app.core.exceptions import APIException
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import func, or_


# Lớp ProjectService: Quản lý toàn bộ logic nghiệp vụ (business logic) liên quan đến Dự án
class ProjectService():
    # Hàm tiện ích dùng để ghi lại lịch sử thao tác của dự án vào DB
    def log_activity(self, db: Session, project_id: int, user_id: int, action: str, desc: str = ""):
        log = ActivityLogModel(
            project_id=project_id,
            user_id=user_id,
            action=action,
            description=desc
        )
        db.add(log)

    # Tạo dự án mới và tự động gán người tạo làm Chủ sở hữu (OWNER)
    def create_project(self, db: Session, project_data: ProjectCreate, current_user: int):
        try:

            new_project = Project(
                name=project_data.name,
                description=project_data.description,
                owner_id=current_user
            )

            db.add(new_project)
            db.flush()

            new_member = ProjectMember(
                user_id=current_user,
                project_id=new_project.id,
                role=ProjectRole.OWNER
            )

            db.add(new_member)
            db.flush()

            self.log_activity(
                db=db,
                project_id=new_project.id,
                user_id=current_user,
                action="create_project",
                desc=f"Khởi tạo dự án {new_project.name}"
            )
            db.commit()
            db.refresh(new_project)
            return new_project
        except Exception as e:
            db.rollback()
            raise APIException(
                status_code=500,
                message="Internal Server Error",
                code=1004,
                error=str(e)
            )

    # Lấy danh sách các dự án mà User hiện tại đang tham gia
    def get_list_project(self, db: Session, current_user_id: int, search: Optional[str] = None, role: Optional[ProjectRole] = None):
        query = db.query(Project).join(ProjectMember).filter(
            Project.is_deleted == False,
            ProjectMember.user_id == current_user_id
                )

        if search:
            query = query.filter(Project.name.ilike(f"%{search}%"))
            
        return query.order_by(Project.name.desc()).all()

    # Xem chi tiết một dự án (phải là thành viên mới được xem)

    def get_project_by_id(self, db: Session, project_id: int, current_user_id: int):
        query = db.query(Project).join(ProjectMember).filter(
            Project.is_deleted == False,
            ProjectMember.user_id == current_user_id,
            Project.id == project_id
        ).first()

        if not query:
            raise APIException(
                status_code=404,
                message="Không tìm thấy dự án hoặc bạn không có quyền truy cập",
                code=1005,
                error="Project not found or access denied"
            )

        return query

    # Cập nhật thông tin dự án (chỉ OWNER mới được phép)
    def update_project(self, db: Session, project_data: ProjectUpdate, project_id: int, current_user_id: int):
        try:
            query_project = db.query(Project).filter(
                Project.id == project_id,
                Project.is_deleted == False
            ).first()

            if not query_project:
                raise APIException(
                    status_code=404,
                    message="Không tìm thấy dự án",
                    code=1005,
                    error="Không tìm thấy dự án"
                )

            if query_project.owner_id != current_user_id:
                raise APIException(
                    status_code=403,
                    message="Bạn không có quyền sửa dự án này",
                    code=1006,
                    error="Bạn không có quyền sửa dự án này"
                )
            if project_data.name is not None:
                query_project.name = project_data.name
            if project_data.description is not None:
                query_project.description = project_data.description

            db.add(query_project)
            self.log_activity(
                db=db,
                project_id=query_project.id,
                user_id=current_user_id,
                action="update_project",
                desc=f"Cập nhật dự án {query_project.name}"
            )
            db.commit()
            db.refresh(query_project)
            return query_project
        except APIException as e:
            db.rollback()
            raise APIException(
                status_code=e.status_code,
                message=e.message,
                code=e.code,
                error=e.error
            )
        except Exception as e:
            db.rollback()
            raise APIException(
                status_code=500,
                message="Internal Server Error",
                code=1004,
                error=str(e)
            )

    # Xóa mềm dự án bằng cách bật cờ is_deleted (chỉ OWNER mới được phép)
    def delete_project(self, db: Session, project_id: int, current_user_id: int):
        try:
            query_project = db.query(Project).filter(
                Project.id == project_id,
                Project.is_deleted == False
            ).first()

            if not query_project:
                raise APIException(
                    status_code=404,
                    message="Không tìm thấy dự án",
                    code=1005,
                    error="Không tìm thấy dự án"
                )

            if query_project.owner_id != current_user_id:
                raise APIException(
                    status_code=403,
                    message="Bạn không có quyền sửa dự án này",
                    code=1006,
                    error="Bạn không có quyền sửa dự án này"
                )
            query_project.is_deleted = True
            query_project.delete_at = datetime.now(timezone.utc)
            db.add(query_project)
            self.log_activity(
                db=db,
                project_id=query_project.id,
                user_id=current_user_id,
                action="delete_project",
                desc=f"Xóa dự án {query_project.name}"
            )
            db.commit()
            db.refresh(query_project)
            return query_project
        except APIException as e:
            db.rollback()
            raise APIException(
                status_code=e.status_code,
                message=e.message,
                code=e.code,
                error=e.error
            )
        except Exception as e:
            db.rollback()
            raise APIException(
                status_code=500,
                message="Internal Server Error",
                code=1004,
                error=str(e)
            )

    # Thêm thành viên mới vào dự án (chỉ OWNER mới được phép thêm, không thêm trùng)
    def add_member_to_project(self, db: Session, project_id: int, current_user_id: int, member_data: ProjectMemberCreate):
        try:
            # 1. Check dự án tồn tại
            query_project = db.query(Project).filter(
                Project.id == project_id, Project.is_deleted == False).first()
            if not query_project:
                raise APIException(
                    status_code=404, message="Không tìm thấy dự án", code=1005)

            # 2. Check quyền OWNER
            if query_project.owner_id != current_user_id:
                raise APIException(
                    status_code=403, message="Bạn không có quyền thêm thành viên", code=1007)

            # 3. Check User có tồn tại trên hệ thống không

            target_user = db.query(Users).filter(
                Users.id == member_data.user_id).first()
            if not target_user:
                raise APIException(
                    status_code=404, message="Người dùng không tồn tại", code="USER_NOT_FOUND")

            if member_data.role == ProjectRole.OWNER:
                raise APIException(
                    status_code=400,
                    message="Một dự án chỉ có thể có duy nhất một Chủ sở hữu (Owner).",
                    code="INVALID_ROLE"
                )
            # 4. Check User đã ở trong dự án chưa
            check_member_existting = db.query(ProjectMember).filter(
                ProjectMember.user_id == member_data.user_id,
                ProjectMember.project_id == project_id
            ).first()
            if check_member_existting:
                raise APIException(
                    status_code=400, message="Thành viên đã tồn tại trong dự án", code=1008)

            # 5. Lưu vào DB
            new_member = ProjectMember(
                project_id=project_id,
                user_id=member_data.user_id,
                role=member_data.role
            )
            db.add(new_member)
            self.log_activity(
                db=db,
                project_id=project_id,
                user_id=current_user_id,
                action="add_member",
                desc=f"Thêm thành viên {target_user.full_name} vào dự án")

            db.commit()
            db.refresh(new_member)
            return new_member
        except APIException as e:
            db.rollback()
            raise e
        except Exception as e:
            db.rollback()
            raise APIException(
                status_code=500, message="Internal Server Error", code=1004, error=str(e))

    # Lấy danh sách các thành viên trong dự án
    def get_member_project(self, db: Session, project_id: int, current_user_id: int):
        try:
            query_is_member = db.query(ProjectMember).filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == current_user_id
            ).first()
            if not query_is_member:
                raise APIException(
                    status_code=403,
                    message="Dự án không tồn tại hoặc bạn không có quyền xem",
                    code=1009
                )

            list_member = db.query(ProjectMember).filter(
                ProjectMember.project_id == project_id
            ).all()
            return list_member
        except APIException as e:
            raise e
        except Exception as e:
            raise APIException(
                status_code=500, message="Internal Server Error", code=1004, error=str(e))

    # Xóa thành viên khỏi dự án (chỉ OWNER mới được phép, không được xóa OWNER cuối cùng)
    def delete_member_project(self, db: Session, project_id: int, current_user_id: int, member_id: int):
        try:
            query_project = db.query(Project).filter(
                Project.id == project_id,
                Project.is_deleted == False
            ).first()
            if not query_project:
                raise APIException(
                    status_code=404,
                    message="Không tìm thấy dự án",
                    code=1005,
                    error="Không tìm thấy dự án"
                )

            if query_project.owner_id != current_user_id:
                raise APIException(
                    status_code=403,
                    message="Bạn không có quyền xóa thành viên",
                    code=1010,
                    error="Bạn không có quyền xóa thành viên"
                )
            if member_id == query_project.owner_id:
                raise APIException(
                    status_code=403,
                    message="Bạn không được xóa chủ sở hữu dự án",
                    code=1011,
                    error="Bạn không được xóa chủ sở hữu dự án"
                )
            query_member = db.query(ProjectMember).filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == member_id
            ).first()
            if not query_member:
                raise APIException(
                    status_code=404,
                    message="Không tìm thấy thành viên",
                    code=1012,
                    error="Không tìm thấy thành viên"
                )
            db.delete(query_member)
            self.log_activity(
                db=db,
                project_id=project_id,
                user_id=current_user_id,
                action="delete_member",
                desc=f"Xóa thành viên {query_member.user_id} khỏi dự án"
            )
            db.commit()
            return query_member
        except APIException as e:
            db.rollback()
            raise e
        except Exception as e:
            db.rollback()
            raise APIException(
                status_code=500, message="Internal Server Error", code=1004, error=str(e))


project_service = ProjectService()
