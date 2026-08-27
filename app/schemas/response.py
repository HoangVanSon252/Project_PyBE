from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, Field

ModelType = TypeVar("ModelType")

# Schema ResponseSchemas: Chuẩn hóa định dạng trả về cho mọi API
class ResponseSchemas(BaseModel, Generic[ModelType]):
    success: bool = Field(True, description="Trạng thái thành công")
    code: str = Field("SUCCESS", description="Mã trạng thái")
    message: str = Field("Thành công", description="Thông báo")
    data: Optional[ModelType] = Field(None, description="Dữ liệu")
    error: Optional[Any] = Field(None, description="Thông báo lỗi")