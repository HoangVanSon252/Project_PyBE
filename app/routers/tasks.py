from fastapi import Depends, APIRouter, HTTPException, UploadFile, File, status, Query
from sqlalchemy.orm import Session
from app.dependencies.deps import get_db, get_current_user
from app.models.user import Users
from app.schemas.task import TaskCreate, TaskPaginationResponse, TaskUpdate, CommentCreate, CommentResponse, AttachmentResponse
from app.services.tasks import TaskService
from app.schemas.response import ResponseSchemas
from app.schemas.task import TaskResponse

router = APIRouter(
    tags=["Tasks"]
)
task_service = TaskService()


@router.post(
    "/projects/{project_id}/tasks",
    response_model=ResponseSchemas[TaskResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Tạo công việc mới",
    description="Tạo một công việc mới trong dự án. Người tạo sẽ tự động được ghi nhận. Có thể gán cho một thành viên khác trong dự án (assignee_id)."
)
def create_task(
    project_id: int,
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    task = task_service.create_task(db=db, current_user_id=current_user.id, project_id=project_id, task_data=task_data)
    return ResponseSchemas(
        success=True,
        code="SUCCESS",
        message="Tạo công việc thành công",
        data=task
    )

@router.get(
    "/projects/{project_id}/tasks",
    response_model=ResponseSchemas[TaskPaginationResponse],
    summary="Lấy danh sách công việc",
    description="Lấy danh sách công việc của dự án. Hỗ trợ phân trang (page, size), bộ lọc (status, priority, assignee_id) và tìm kiếm (search)."
)
def get_project_tasks(
    project_id: int,
    status: str = None,
    priority: str = None,
    assignee_id: int = None,
    search: str = None,
    page: int = 1,
    size: int = 10,
    sort_by: str = "created_at",
    order: str = "desc",
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    tasks = task_service.get_project_tasks(
        db=db, project_id=project_id, current_user_id=current_user.id,
        status=status, priority=priority, assignee_id=assignee_id,
        search=search, page=page, size=size, sort_by=sort_by, order=order
    )
    return ResponseSchemas(
        success=True,
        code="SUCCESS",
        message="Lấy danh sách công việc thành công",
        data=tasks
    )

@router.get(
    "/tasks/{task_id}",
    response_model=ResponseSchemas[TaskResponse],
    summary="Xem chi tiết công việc",
    description="Lấy thông tin chi tiết của một công việc. Người dùng phải là thành viên của dự án chứa công việc này."
)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    task = task_service.get_task_by_id(db=db, task_id=task_id, current_user_id=current_user.id)
    return ResponseSchemas(
        success=True,
        code="SUCCESS",
        message="Lấy công việc thành công",
        data=task
    )

@router.patch(
    "/tasks/{task_id}",
    response_model=ResponseSchemas[TaskResponse],
    summary="Cập nhật công việc",
    description="Cập nhật một phần thông tin của công việc (chỉ gửi những trường cần sửa). Bất kỳ thành viên nào cũng có thể cập nhật."
)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    task = task_service.update_task(db=db, task_id=task_id, current_user_id=current_user.id, task_data=task_data)
    return ResponseSchemas(
        success=True,
        code="SUCCESS",
        message="Cập nhật công việc thành công",
        data=task
    )

@router.delete(
    "/tasks/{task_id}",
    response_model=ResponseSchemas[bool],
    summary="Xóa công việc",
    description="Xóa vĩnh viễn một công việc. Yêu cầu: Người xóa phải là Chủ dự án (OWNER) HOẶC người đã tạo ra công việc đó."
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    result = task_service.delete_task(db=db, task_id=task_id, current_user_id=current_user.id)
    return ResponseSchemas(
        success=True,
        code="SUCCESS",
        message="Xóa công việc thành công",
        data=result
    )

@router.post(
    "/tasks/{task_id}/comments",
    response_model=ResponseSchemas[CommentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Thêm bình luận",
    description="Thêm một bình luận mới vào công việc. Chỉ thành viên dự án mới được bình luận."
)
def add_comment(
    task_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    comment = task_service.add_comment(db=db, task_id=task_id, current_user_id=current_user.id, comment_data=comment_data)
    return ResponseSchemas(
        success=True,
        code="SUCCESS",
        message="Thêm bình luận thành công",
        data=comment
    )

@router.post(
    "/tasks/{task_id}/attachments",
    response_model=ResponseSchemas[AttachmentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload file đính kèm",
    description="Tải lên file đính kèm cho công việc (Giới hạn: <= 5MB. Loại: jpg, png, pdf, docx)."
)
def upload_attachment(
    task_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    attachment = task_service.upload_attachment(db=db, task_id=task_id, current_user_id=current_user.id, file=file)
    return ResponseSchemas(
        success=True,
        code="SUCCESS",
        message="Tải file lên thành công",
        data=attachment
    )
    