from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, status
from app.schemas.user import UserResponse, UserCreate
from app.models.user import Users
from app.schemas.response import ResponseSchemas
from sqlalchemy.orm import Session
from app.core.exceptions import APIException
from app.core.security import get_hashed_password, verify_password, create_access_token, create_refresh_token
from app.schemas.token import RefreshTokenRequest
from jose import jwt
from app.core.config import settings
from app.dependencies.deps import get_db
from datetime import timedelta, datetime, timezone
router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post(
    "/register",
    response_model=ResponseSchemas[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản mới",
    description="Tạo một tài khoản người dùng mới. Yêu cầu email chưa tồn tại trong hệ thống."
)
# API Đăng ký tài khoản (Register)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        user_exits = db.query(Users).filter(Users.email == user_data.email).first()
        if user_exits:
            raise APIException(
                status_code=status.HTTP_400_BAD_REQUEST,
                code="USER_ALREADY_EXISTS",
                message="Email đã tồn tại",
            )
        hashed_password = get_hashed_password(user_data.password)
        user = Users(
            email=user_data.email,
            password_hash=hashed_password,
            full_name=user_data.full_name,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return ResponseSchemas(
            success=True,
            message="Đăng ký thành công",
            data=user
        )
    except Exception as e:
        db.rollback()
        raise e

login_attempts  = {}
MAX_ATTEMPTS = 5
LOCK_TIME = timedelta(minutes=5)

@router.post(
    "/login",
    summary="Đăng nhập",
    description="Xác thực người dùng bằng email và mật khẩu, trả về Access Token và Refresh Token. Cảnh báo: Tạm khóa tài khoản 5 phút nếu đăng nhập sai quá 5 lần."
)
# API Đăng nhập lấy Token (Login) kèm tính năng giới hạn Rate Limit
def login(login_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    time_now = datetime.now(timezone.utc)
    email_to_check = login_data.username

    info_attempts = login_attempts.get(email_to_check)
    if info_attempts and info_attempts["count"] > MAX_ATTEMPTS:
        if time_now < info_attempts["locked"]:
            raise APIException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                code="RATE_LIMIT",
                message="Bạn đã nhập sai quá 5 lần. Vui lòng thử lại sau 5 phút."
            )
        else:
            login_attempts[email_to_check] = {"count": 0, "locked": None}
    user = db.query(Users).filter(Users.email == login_data.username).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        if email_to_check not in login_attempts:
            login_attempts[email_to_check] = {"count": 1, "locked": None}
        else:
            login_attempts[email_to_check]["count"] += 1
            if login_attempts[email_to_check]["count"] > MAX_ATTEMPTS:
                login_attempts[email_to_check]["locked"] = time_now + LOCK_TIME
        raise APIException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="LOGIN_FAILED",
            message="Email hoặc mật khẩu không chính xác",
        )
    if not user.is_active:
        raise APIException(
            status_code=status.HTTP_403_FORBIDDEN,
            code="ACCOUNT_INACTIVE",
            message="Tài khoản của bạn đã bị khóa",
        )
    access_token = create_access_token(data={"id": str(user.id), "role": str(user.role)})
    refresh_token = create_refresh_token(data={"id": str(user.id), "role": str(user.role)})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name
        }
    }


@router.post(
    "/refresh-token",
    response_model=ResponseSchemas[dict],
    summary="Cấp lại Access Token",
    description="Sử dụng Refresh Token hợp lệ để lấy Access Token mới."
)
# API Cấp lại Access Token mới dựa vào Refresh Token
def refresh_token(refresh_token_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token=refresh_token_data.refresh_token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("id")
        token_type = payload.get("type")
        if token_type != "refresh" or user_id is None:
            raise APIException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                code="INVALID_TOKEN",
                message="Token không hợp lệ"
            )
        user = db.query(Users).filter(Users.id == int(user_id)).first()
        if not user:
            raise APIException(
                status_code=status.HTTP_404_NOT_FOUND,
                code="USER_NOT_FOUND",
                message="Người dùng không tồn tại"
            )
        access_token = create_access_token(data={"id": str(user.id), "role": str(user.role)})
        return ResponseSchemas(
            success=True,
            message="Token đã được làm mới thành công",
            data={
                "access_token": access_token,
                "token_type": "Bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name
                }
            }
        )
    except jwt.ExpiredSignatureError:
        raise APIException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="TOKEN_EXPIRED",
            message="Token đã hết hạn"
        )
    except jwt.JWTError:
        raise APIException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="INVALID_TOKEN",
            message="Token không hợp lệ"
        )