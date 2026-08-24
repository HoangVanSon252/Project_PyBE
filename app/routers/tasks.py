from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.dependencies.deps import get_db, get_current_user
from app.models.user import Users
from app.schemas.task import TaskCreate
from app.services.tasks import TaskService
from app.schemas.response import ResponseSchemas
from app.schemas.task import TaskResponse

router = APIRouter(
    tags=["Tasks"]
)
task_service = TaskService()


@router.post("/projects/{project_id}/tasks", response_model=ResponseSchemas[TaskResponse])
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