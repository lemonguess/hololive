from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

class ValidationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            if e.status_code == HTTP_422_UNPROCESSABLE_ENTITY:
                raise HTTPException(
                    status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="请求参数校验失败"
                )
            raise e