import app.models
from app.schemas.response import ResponseSchemas
from app.core.exceptions import setup_exception_handler
from fastapi import FastAPI
from app.db.database import engine
from app.db.database import Base
from app.routers import auth, users, projects, tasks
Base.metadata.create_all(bind=engine)

app = FastAPI()
setup_exception_handler(app=app)


# API Health check: Dùng để kiểm tra xem server có đang hoạt động bình thường không
@app.get("/health", response_model=ResponseSchemas[dict])
def health_test():
    return ResponseSchemas(
        success=True,
        code="OK",
        message="API chạy thành ổn định",
        data={"status":"ok"},
        error=None
    )
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)