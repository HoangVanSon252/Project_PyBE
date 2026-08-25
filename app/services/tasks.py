from app.core.exceptions import APIException
from typing import Optional
from sqlalchemy import or_, desc, asc
from app.models.comment import TaskComment
from app.models.attachment import TaskAttachment
from app.schemas.task import CommentCreate, TaskStatus, TaskPriority
import os
import shutil
from fastapi import UploadFile
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from app.models.project import ProjectMember
from sqlalchemy.orm import Session
class TaskService:
    def create_task(self, db: Session, project_id: int, current_user_id: int, task_data: TaskCreate):
        try:
            is_member = db.query(ProjectMember).filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == current_user_id
            ).first()

            if not is_member:
                raise APIException(
                    status_code=403,
                    code="PROJECT_NOT_FOUND",
                    message="Không tìm thấy dự án hoặc bạn không có quyền truy cập",
                    error="FORBIDDEN"
                )


            # check xẽm có người làm chưa nếu chưa thì xem người đó có trong dự án không
            if task_data.assignee_id is not None:
                is_assignee_member = db.query(ProjectMember).filter(
                    ProjectMember.project_id == project_id,
                    ProjectMember.user_id == task_data.assignee_id
                ).first()

                if not is_assignee_member:
                    raise APIException(
                        status_code=403,
                        code="ASSIGNEE_NOT_FOUND",
                        message="Người được giao không có trong dự án",
                        error="FORBIDDEN"
                    )
            new_task = Task(
                project_id = project_id,
                title = task_data.title,
                description = task_data.description,
                assignee_id = task_data.assignee_id,
                creator_id = current_user_id,
                status = task_data.status,
                priority = task_data.priority,
                due_date = task_data.due_date
            )
            db.add(new_task)
            db.commit()
            db.refresh(new_task)
            return new_task
        
        except APIException as e:
            db.rollback()
            raise e
        except Exception as e:
            db.rollback()
            raise APIException(
                status_code=500,
                code="INTERNAL_SERVER_ERROR",
                message="Lỗi server",
                error=str(e)
            )

    def get_project_tasks(
        self, db: Session, project_id: int, current_user_id: int,
        status: Optional[TaskStatus] = None, priority: Optional[TaskPriority] = None,
        assignee_id: Optional[int] = None, search: Optional[str] = None,
        page: int = 1, size: int = 10, sort_by: str = "created_at", order: str = "desc"
    ):
        try:
            # Check member
            is_member = db.query(ProjectMember).filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == current_user_id
            ).first()
            if not is_member:
                raise APIException(403, "FORBIDDEN", "Bạn không có quyền truy cập dự án này")
            query = db.query(Task).filter(Task.project_id == project_id)
            if status:
                query = query.filter(Task.status == status)
            if priority:
                query = query.filter(Task.priority == priority)
            if assignee_id:
                query = query.filter(Task.assignee_id == assignee_id)
            if search:
                query = query.filter(Task.title.ilike(f"%{search}%"))
            # Sorting
            sort_column = getattr(Task, sort_by, Task.created_at)
            if order.lower() == "asc":
                query = query.order_by(asc(sort_column))
            else:
                query = query.order_by(desc(sort_column))
            total = query.count()
            tasks = query.offset((page - 1) * size).limit(size).all()
            
            return {"items": tasks, "total": total, "page": page, "size": size}
        except APIException as e:
            raise e
        except Exception as e:
            raise APIException(500, "INTERNAL_SERVER_ERROR", "Lỗi server", str(e))

    def update_task(self, db: Session, task_id: int, current_user_id: int, task_data: TaskUpdate):
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                raise APIException(404, "NOT_FOUND", "Không tìm thấy công việc")

            is_member = db.query(ProjectMember).filter(
                ProjectMember.project_id == task.project_id,
                ProjectMember.user_id == current_user_id
            ).first()
            if not is_member:
                raise APIException(403, "FORBIDDEN", "Bạn không có quyền truy cập công việc này")

            if task_data.assignee_id is not None and task_data.assignee_id != task.assignee_id:
                is_assignee_member = db.query(ProjectMember).filter(
                    ProjectMember.project_id == task.project_id,
                    ProjectMember.user_id == task_data.assignee_id
                ).first()
                if not is_assignee_member:
                    raise APIException(403, "ASSIGNEE_NOT_FOUND", "Người được giao không có trong dự án")

            update_data = task_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(task, key, value)

            db.commit()
            db.refresh(task)
            return task
        except APIException as e:
            db.rollback()
            raise e
        except Exception as e:
            db.rollback()
            raise APIException(500, "INTERNAL_SERVER_ERROR", "Lỗi server", str(e))

    def get_task_by_id(self, db: Session, task_id: int, current_user_id: int):
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                raise APIException(404, "NOT_FOUND", "Không tìm thấy công việc")
            
            is_member = db.query(ProjectMember).filter(
                ProjectMember.project_id == task.project_id,
                ProjectMember.user_id == current_user_id
            ).first()
            if not is_member:
                raise APIException(403, "FORBIDDEN", "Bạn không có quyền truy cập công việc này")
            
            return task
        except APIException as e:
            raise e
        except Exception as e:
            raise APIException(500, "INTERNAL_SERVER_ERROR", "Lỗi server", str(e))

    def delete_task(self, db: Session, task_id: int, current_user_id: int):
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                raise APIException(404, "NOT_FOUND", "Không tìm thấy công việc")
            from app.models.project import Project, ProjectRole
            project_member = db.query(ProjectMember).filter(
                ProjectMember.project_id == task.project_id,
                ProjectMember.user_id == current_user_id
            ).first()
            
            if not project_member:
                raise APIException(403, "FORBIDDEN", "Bạn không có quyền truy cập dự án này")
            
            if project_member.role != ProjectRole.OWNER and task.creator_id != current_user_id:
                raise APIException(403, "FORBIDDEN", "Chỉ Owner hoặc người tạo mới được xóa công việc")
            
            db.delete(task)
            db.commit()
            return True
        except APIException as e:
            db.rollback()
            raise e
        except Exception as e:
            db.rollback()
            raise APIException(500, "INTERNAL_SERVER_ERROR", "Lỗi server", str(e))

    def add_comment(self, db: Session, task_id: int, current_user_id: int, comment_data: CommentCreate):
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                raise APIException(404, "NOT_FOUND", "Không tìm thấy công việc")
            
            is_member = db.query(ProjectMember).filter(
                ProjectMember.project_id == task.project_id,
                ProjectMember.user_id == current_user_id
            ).first()
            if not is_member:
                raise APIException(403, "FORBIDDEN", "Bạn không có quyền comment")
            new_comment = TaskComment(
                task_id=task_id,
                user_id=current_user_id,
                content=comment_data.content
            )
            db.add(new_comment)
            db.commit()
            db.refresh(new_comment)
            return new_comment
        except APIException as e:
            db.rollback()
            raise e
        except Exception as e:
            db.rollback()
            raise APIException(500, "INTERNAL_SERVER_ERROR", "Lỗi server", str(e))

    def upload_attachment(self, db: Session, task_id: int, current_user_id: int, file: UploadFile):
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                raise APIException(404, "NOT_FOUND", "Không tìm thấy công việc")
            
            is_member = db.query(ProjectMember).filter(
                ProjectMember.project_id == task.project_id,
                ProjectMember.user_id == current_user_id
            ).first()
            if not is_member:
                raise APIException(403, "FORBIDDEN", "Bạn không có quyền tải file")
            
            ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".pdf", ".docx"]
            ext = os.path.splitext(file.filename)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise APIException(400, "INVALID_FILE_TYPE", "Loại file không hợp lệ")
            
            upload_dir = "uploads"
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, f"{task_id}_{file.filename}")
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            file_size = os.path.getsize(file_path)
            if file_size > 5 * 1024 * 1024:
                os.remove(file_path)
                raise APIException(400, "FILE_TOO_LARGE", "File không được vượt quá 5MB")
            
            new_attachment = TaskAttachment(
                task_id=task_id,
                uploader_id=current_user_id,
                file_name=file.filename,
                file_url=f"/uploads/{task_id}_{file.filename}",
                file_type=ext,
                file_size=file_size
            )
            db.add(new_attachment)
            db.commit()
            db.refresh(new_attachment)
            return new_attachment
        except APIException as e:
            db.rollback()
            raise e
        except Exception as e:
            db.rollback()
            raise APIException(500, "INTERNAL_SERVER_ERROR", "Lỗi server", str(e))