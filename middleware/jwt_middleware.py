from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_401_UNAUTHORIZED
import jwt
from jwt.exceptions import InvalidTokenError
from config import app_config

class JWTMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.secret_key = app_config.jwt.JWT_SECRET_KEY
        # 检查 JWT_ALGORITHM 是否存在
        if not hasattr(app_config.jwt, 'JWT_ALGORITHM'):
            raise ValueError("JWT_ALGORITHM is not configured in app_config.jwt")
        self.algorithm = app_config.jwt.JWT_ALGORITHM

    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header"
            )

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            request.state.user_uuid = payload.get("user_uuid")
        except InvalidTokenError:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        response = await call_next(request)
        return response