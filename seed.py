from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.user import Users, UserRole
from app.models.project import Project, ProjectMember, ProjectRole
from app.models.task import Task, TaskStatus, TaskPriority
from app.core.security import get_hashed_password
from datetime import datetime, timedelta

def seed_data():
    print("Bắt đầu khởi tạo dữ liệu mẫu (Seeding)...")
    db = SessionLocal()
    
    # Tạo bảng nếu chưa có
    Base.metadata.create_all(bind=engine)

    try:
        # Check nếu đã có data thì bỏ qua
        if db.query(Users).first():
            print("Dữ liệu đã tồn tại trong Database. Bỏ qua seeding.")
            return

        print("Đang tạo 5 Users...")
        users = [
            Users(email="admin@gmail.com", password_hash=get_hashed_password("12345678"), full_name="System Admin", role=UserRole.ADMIN),
            Users(email="user1@gmail.com", password_hash=get_hashed_password("12345678"), full_name="User Một", role=UserRole.USER),
            Users(email="user2@gmail.com", password_hash=get_hashed_password("12345678"), full_name="User Hai", role=UserRole.USER),
            Users(email="user3@gmail.com", password_hash=get_hashed_password("12345678"), full_name="User Ba", role=UserRole.USER),
            Users(email="user4@gmail.com", password_hash=get_hashed_password("12345678"), full_name="User Bốn", role=UserRole.USER)
        ]
        db.add_all(users)
        db.commit()

        print("Đang tạo 2 Projects...")
        # Lấy admin làm OWNER
        admin = db.query(Users).filter_by(email="admin@gmail.com").first()
        user1 = db.query(Users).filter_by(email="user1@gmail.com").first()
        user2 = db.query(Users).filter_by(email="user2@gmail.com").first()
        user3 = db.query(Users).filter_by(email="user3@gmail.com").first()
        user4 = db.query(Users).filter_by(email="user4@gmail.com").first()
        project1 = Project(name="Dự án Alpha", description="Mô tả dự án Alpha", owner_id=admin.id)
        project2 = Project(name="Dự án Beta", description="Mô tả dự án Beta", owner_id=user1.id)
        db.add_all([project1, project2])
        db.commit()

        # Thêm các thành viên vào dự án
        print("Đang thêm thành viên vào Projects...")
        members = [
            ProjectMember(project_id=project1.id, user_id=admin.id, role=ProjectRole.OWNER),
            ProjectMember(project_id=project1.id, user_id=user1.id, role=ProjectRole.MEMBER),
            ProjectMember(project_id=project1.id, user_id=user2.id, role=ProjectRole.MEMBER),
            ProjectMember(project_id=project1.id, user_id=user3.id, role=ProjectRole.MEMBER),
            ProjectMember(project_id=project1.id, user_id=user4.id, role=ProjectRole.MEMBER),
        
            ProjectMember(project_id=project2.id, user_id=user1.id, role=ProjectRole.OWNER),
            ProjectMember(project_id=project2.id, user_id=user3.id, role=ProjectRole.MEMBER)
        ]
        db.add_all(members)
        db.commit()

        # Thêm Tasks
        print("Đang tạo 10 Tasks...")
        tasks = []
        for i in range(1, 6):
            tasks.append(
                Task(
                    title=f"Công việc Alpha {i}", 
                    description=f"Chi tiết công việc {i}", 
                    project_id=project1.id, 
                    creator_id=admin.id,
                    assignee_id=user1.id if i % 2 == 0 else user2.id,
                    status=TaskStatus.TODO if i > 2 else TaskStatus.IN_PROGRESS,
                    priority=TaskPriority.HIGH if i == 1 else TaskPriority.MEDIUM,
                    due_date=datetime.now() + timedelta(days=i)
                )
            )
        for i in range(1, 6):
            tasks.append(
                Task(
                    title=f"Công việc Beta {i}", 
                    description=f"Chi tiết công việc {i}", 
                    project_id=project2.id, 
                    creator_id=user1.id,
                    assignee_id=user3.id,
                    status=TaskStatus.DONE if i == 1 else TaskStatus.TODO,
                    priority=TaskPriority.LOW,
                    due_date=datetime.now() + timedelta(days=i+5)
                )
            )
        
        db.add_all(tasks)
        db.commit()
        
        print("Khởi tạo dữ liệu thành công! ✅")

    except Exception as e:
        db.rollback()
        print(f"Lỗi khởi tạo dữ liệu: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
