from app.models.task import Task, TaskPriority, TaskStatus
from app.models.project import Project, ProjectRole, ProjectMember
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import Users, UserRole
from app.core.security import get_hashed_password
from app.models.activity import ActivityLogModel
def seed_data():
    db: Session = SessionLocal()
    try:
        # Xóa tất cả dữ liệu cũ để bắt đầu lại từ đầu
        db.query(ProjectMember).delete()
        db.query(Task).delete()
        db.query(ActivityLogModel).delete()
        db.query(Project).delete()
        db.query(Users).delete()
        hashed_pass = get_hashed_password("123456")
        user1 = Users(
            email ="hoangvanson2552@gmail.com",
            password_hash =hashed_pass,
            full_name="HoangVanSon",
            role = UserRole.ADMIN
        )
        db.add_all([user1])
        db.commit()
        print("User da duoc tao thanh cong")
        
        project1 = Project(
            name = "Project 1",
            description = "Project 1",
            owner_id = user1.id
        )
        project2 = Project(
            name = "Project 2",
            description = "Project 2",
            owner_id = user1.id
        )
        db.add_all([project1, project2])
        db.commit()
        print("Project da duoc tao thanh cong")

        project_member1 = ProjectMember(
            project_id = project1.id,
            user_id = user1.id,
            role = ProjectRole.OWNER
        )
        project_member3 = ProjectMember(
            project_id = project2.id,
            user_id = user1.id,
            role = ProjectRole.OWNER
        )
        db.add_all([project_member1, project_member3])
        db.commit()
        print("ProjectMember da duoc tao thanh cong")


        task1 = Task(
            project_id = project1.id,
            title = "Task 1",
            description = "Task 1",
            assignee_id = user1.id,
            status = TaskStatus.TODO,
            priority = TaskPriority.HIGH,
            due_date = "2022-12-31"
        )
        task2 = Task(
            project_id = project1.id,
            title = "Task 2",
            description = "Task 2",
            assignee_id = user1.id,
            status = TaskStatus.IN_PROGRESS,
            priority = TaskPriority.MEDIUM,
            due_date = "2022-12-31"
        )
        task3 = Task(
            project_id = project2.id,
            title = "Task 3",
            description = "Task 3",
            assignee_id = user1.id,
            status = TaskStatus.DONE,
            priority = TaskPriority.LOW,
            due_date = "2022-12-31"
        )
        task4 = Task(
            project_id = project2.id,
            title = "Task 4",
            description = "Task 4",
            assignee_id = user1.id,
            status = TaskStatus.TODO,
            priority = TaskPriority.HIGH,
            due_date = "2022-12-31"
        )
        db.add_all([task1, task2, task3, task4])
        db.commit()
        print("Task da duoc tao thanh cong")

        # test_xóa
        project = db.query(Project).filter(Project.id == 1).first()
        if project:
            db.delete(project)
            db.commit()
            print("Project1 da duoc xoa thanh cong")
    except Exception as e:
        print(f"Loi khi them du lieu: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()