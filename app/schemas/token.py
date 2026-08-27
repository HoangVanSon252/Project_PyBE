from pydantic import BaseModel, Field

# Schema RefreshTokenRequest: Validate payload khi gửi request lấy lại Access Token
class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Token làm mới")
    