from typing import List
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import Request

class APIException(Exception):
    def __init__(self, status_code: int, code:str, message: str, error: List = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.error = error

def setup_exception_handler(app):
    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "code": exc.code,
                "message": exc.message,
                "data": None,
                "error": exc.error
            }
        )
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "code": "VALIDATION_ERROR",
                "message": "Dữ liệu không hợp lệ",
                "data": None,
                "error": exc.errors()
            }
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "code": "HTTP_EXCEPTION",
                "message": exc.detail,
                "data": None,
                "error": None
            }
        )
    @app.exception_handler(Exception)
    async def exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Đã có lỗi xảy ra",
                "data": None,
                "error": None
            }
        )