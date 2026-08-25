from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from app.db.database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from app.core.security import settings
from app.models.user import Users, UserRole
from app.core.exceptions import APIException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("id")
        token_type = payload.get("type")

        if token_type != "access":
            raise APIException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                code="UNAUTHORIZED",
                message="Thông tin xác thực không hợp lệ"
            )
        if user_id is None:
            raise APIException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                code="UNAUTHORIZED",
                message="Không tìm thấy thông tin người dùng"
            )
        user = db.query(Users).filter(Users.id == user_id).first()
        if not user:
            raise APIException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                code="UNAUTHORIZED",
                message="Không tìm thấy thông tin người dùng"
            )
        if not user.is_active:
            raise APIException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                code="UNAUTHORIZED",
                message="Tài khoản của bạn đã bị khóa"
            )
        return user
    except JWTError:
        raise APIException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="UNAUTHORIZED",
            message="Thông tin xác thực không hợp lệ"
        )
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="INTERNAL_SERVER_ERROR",
            message="Đã có lỗi xảy ra",
            error=str(e)
        )


def get_current_user_is_admin(
    current_user: Users = Depends(get_current_user)
):
    if current_user.role != UserRole.ADMIN:
        raise APIException(
            status_code=status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN",
            message="Bạn không có quyền truy cập tài nguyên này",
        )
    return current_user
