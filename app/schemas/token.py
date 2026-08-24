from pydantic import BaseModel, Field

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Token làm mới")
    