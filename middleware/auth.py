from starlette.responses import JSONResponse

from models.enums import UserRoleType
from config import app_config
from jose import JWTError, jwt
from fastapi import Request
from fastapi.security import HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import Depends
from functools import wraps
from fastapi.security import OAuth2PasswordBearer
bearer_scheme = HTTPBearer()
SECRET_KEY = app_config.jwt.jwt_secret_key
ALGORITHM = app_config.jwt.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = int(app_config.jwt.access_token_expire_minutes)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user_uuid(request: Request):
    try:
        token = request.headers.get("Authorization").split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid: str = payload.get("useruuid")
        if user_uuid is None:
            raise JWTError("JWT解析错误")
    except JWTError:
        raise JWTError("JWT解析错误")
    return user_uuid

def require_roles(allowed_roles: UserRoleType = None):
    """角色鉴权装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            try:
                token = request.headers.get("Authorization").split(" ")[1]
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_role = payload.get("role")
            except Exception as e:
                print(e)
                return JSONResponse(
                    status_code=401,
                    content={
                        "code": 1,
                        "msg": "Token校验失败",
                        "data": None
                    }
                )
            # 验证过期时间
            if datetime.utcfromtimestamp(payload.get("exp")) < datetime.utcnow():
                return JSONResponse(
                    status_code=401,
                    content={
                        "code": 1,
                        "msg": "Token已过期",
                        "data": None
                    }
                )
            # 验证角色
            if allowed_roles:
                if user_role > allowed_roles.value:
                    return JSONResponse(
                        status_code=401,
                        content={
                            "code": 1,
                            "msg": f"需要角色权限>=【{allowed_roles.name}】",
                            "data": None
                        }
                    )
            # 继续执行原函数
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator