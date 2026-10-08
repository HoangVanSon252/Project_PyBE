import app.models
from app.schemas.response import ResponseSchemas
from app.core.exceptions import setup_exception_handler
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.middleware import SecurityMiddleware
from app.db.database import engine
from app.dependencies.deps import get_current_user
from app.routers import auth, users, projects, tasks

app = FastAPI(title="Project Management API", version="1.0.0", docs_url="/docs" if settings.ENVIRONMENT != "production" else None)
app.add_middleware(SecurityMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=[str(x).rstrip('/') for x in settings.BACKEND_CORS_ORIGINS], allow_credentials=True, allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"], allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"])
setup_exception_handler(app=app)


# API Health check: Dùng để kiểm tra xem server có đang hoạt động bình thường không
@app.get("/health", response_model=ResponseSchemas[dict])
def health_test():
    return ResponseSchemas(
        success=True,
        code="OK",
        message="API chạy thành ổn định",
        data={"status": "ok"},
        error=None
    )


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
