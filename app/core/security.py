from datetime import timedelta, datetime, timezone
from app.core.config import settings
from jose import jwt
import bcrypt

# Hàm kiểm tra tính hợp lệ của mật khẩu (so sánh mật khẩu thô và mật khẩu đã băm)
def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


# Hàm băm mật khẩu bằng thuật toán bcrypt
def get_hashed_password(password: str):
    salt = bcrypt.gensalt()
    pass_bytes = password.encode("utf-8")
    hashed_password = bcrypt.hashpw(pass_bytes, salt)
    return hashed_password.decode("utf-8")

# Hàm tạo Access Token sử dụng JSON Web Token (JWT)
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(
            timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Hàm tạo Refresh Token để cấp lại Access Token khi hết hạn
def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + \
            timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
