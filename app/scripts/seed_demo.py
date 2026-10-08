"""Seed a complete, repeatable local dataset for every application table."""
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.security import get_hashed_password
from app.db.database import SessionLocal
from app.models.activity import ActivityLogModel
from app.models.attachment import TaskAttachment
from app.models.comment import TaskComment
from app.models.project import Project, ProjectMember, ProjectRole
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.user import Users, UserRole

USERS = [
    ("admin@example.com", "Admin User", UserRole.ADMIN, "SEED_ADMIN_PASSWORD"),
    ("manager@example.com", "Manager User", UserRole.MANAGER, "SEED_MANAGER_PASSWORD"),
    ("user@example.com", "Regular User", UserRole.USER, "SEED_USER_PASSWORD"),
]


def ensure_user(db, email, full_name, role, password_env):
    user = db.query(Users).filter_by(email=email).first()
    if not user:
        user = Users(email=email, full_name=full_name, role=role, is_active=True,
                     password_hash=get_hashed_password(os.getenv(password_env, "ChangeMe123!")))
        db.add(user)
        db.flush()
    else:
        user.full_name, user.role, user.is_active = full_name, role, True
    return user


def ensure_project(db, name, description, owner):
    project = db.query(Project).filter_by(name=name).first()
    if not project:
        project = Project(name=name, description=description, owner_id=owner.id, is_deleted=False)
        db.add(project)
        db.flush()
    return project


def ensure_member(db, project, user, role):
    member = db.query(ProjectMember).filter_by(project_id=project.id, user_id=user.id).first()
    if member:
        member.role = role
    else:
        db.add(ProjectMember(project_id=project.id, user_id=user.id, role=role))


def ensure_task(db, project, title, description, creator, assignee, status, priority, due_days):
    task = db.query(Task).filter_by(project_id=project.id, title=title).first()
    if not task:
        task = Task(
            project_id=project.id, title=title, description=description,
            creator_id=creator.id, assignee_id=assignee.id if assignee else None,
            status=status, priority=priority,
            due_date=datetime.now(timezone.utc) + timedelta(days=due_days),
        )
        db.add(task)
        db.flush()
    return task


def ensure_comment(db, task, user, content):
    if not db.query(TaskComment).filter_by(task_id=task.id, user_id=user.id, content=content).first():
        db.add(TaskComment(task_id=task.id, user_id=user.id, content=content))


def ensure_activity(db, project, user, action, description):
    if not db.query(ActivityLogModel).filter_by(project_id=project.id, action=action, description=description).first():
        db.add(ActivityLogModel(project_id=project.id, user_id=user.id, action=action, description=description))


def ensure_attachment(db, task, user, file_name, content):
    directory = Path(__file__).resolve().parents[1] / "uploads" / "demo"
    directory.mkdir(parents=True, exist_ok=True)
    file_path = directory / file_name
    if not file_path.exists():
        file_path.write_bytes(content)
    file_url = f"/uploads/demo/{file_name}"
    if not db.query(TaskAttachment).filter_by(task_id=task.id, file_url=file_url).first():
        db.add(TaskAttachment(task_id=task.id, uploader_id=user.id, file_name=file_name,
                              file_url=file_url, file_type=file_path.suffix,
                              file_size=file_path.stat().st_size))


def main():
    db = SessionLocal()
    try:
        admin, manager, user = [ensure_user(db, *item) for item in USERS]
        website = ensure_project(db, "Website Ra Mat San Pham",
                                 "Ke hoach ra mat website va noi dung marketing.", manager)
        mobile = ensure_project(db, "Ung Dung Di Dong",
                                "Theo doi phat trien phien ban mobile dau tien.", admin)
        for project, memberships in (
            (website, ((manager, ProjectRole.OWNER), (admin, ProjectRole.MEMBER), (user, ProjectRole.VIEWER))),
            (mobile, ((admin, ProjectRole.OWNER), (manager, ProjectRole.MEMBER), (user, ProjectRole.MEMBER))),
        ):
            for member, role in memberships:
                ensure_member(db, project, member, role)
        db.flush()

        design = ensure_task(db, website, "Hoan thien giao dien trang chu",
                             "Hoan thien desktop va mobile cho trang chu.", manager, user,
                             TaskStatus.IN_PROGRESS, TaskPriority.HIGH, 3)
        seo = ensure_task(db, website, "Viet noi dung SEO",
                          "Chuan bi noi dung cho cac trang dich vu.", manager, admin,
                          TaskStatus.TODO, TaskPriority.MEDIUM, 7)
        api = ensure_task(db, mobile, "Xay dung API dang nhap",
                          "Tich hop dang nhap cookie va refresh token.", admin, manager,
                          TaskStatus.DONE, TaskPriority.HIGH, -2)
        testing = ensure_task(db, mobile, "Kiem thu chuc nang thong bao",
                              "Lap danh sach test case cho thong bao.", admin, user,
                              TaskStatus.TODO, TaskPriority.LOW, 10)

        ensure_comment(db, design, user, "Toi da hoan thanh phan giao dien mobile.")
        ensure_comment(db, design, manager, "Tot, vui long gui ban preview truoc khi merge.")
        ensure_comment(db, api, manager, "API da duoc kiem thu va hoat dong on dinh.")
        ensure_comment(db, testing, admin, "Hay uu tien kiem thu tren Android truoc.")
        ensure_attachment(db, design, user, "homepage-wireframe.txt", b"Demo homepage wireframe.\n")
        ensure_attachment(db, api, admin, "api-login-notes.txt", b"Demo API login notes.\n")

        ensure_activity(db, website, manager, "create_project", "Khoi tao du an Website Ra Mat San Pham")
        ensure_activity(db, website, user, "update_task", "Cap nhat tien do giao dien trang chu")
        ensure_activity(db, mobile, admin, "create_project", "Khoi tao du an Ung Dung Di Dong")
        ensure_activity(db, mobile, manager, "complete_task", "Hoan thanh API dang nhap")
        db.commit()
        print("Seeded every table: users, projects, members, tasks, comments, attachments, activity logs.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
