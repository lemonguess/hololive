from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette import status
from utils.response_util import ResponseUtil

class ValidationMiddleware:
    async def __call__(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except RequestValidationError as exc:
            return ResponseUtil.error(
                message='参数校验错误',
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )