from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from config import app_config
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
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # username: str = payload.get("username")
        user_uuid: str = payload.get("user_uuid")
        if user_uuid is None:
            raise JWTError("JWT解析错误")
    except JWTError:
        raise JWTError("JWT解析错误")
    return user_uuid

# def check_permission(permission: str, user: User = Depends(get_current_user)):
#     for role in user.roles:
#         for perm in role.permissions:
#             if perm.name == permission:
#                 return True
#     raise HTTPException(status_code=403, detail="Permission denied")