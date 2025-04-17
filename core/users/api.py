import traceback
from datetime import timedelta

from fastapi import (
    APIRouter, Request
)
import logging
from starlette import status
from starlette.responses import JSONResponse
from core.users.interface import UserInterface
from models.enums import UserRoleType
from utils import AsyncDatabaseManagerInstance
from middleware.auth import (
    verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash
)
from core.users.schemas import UserTokenAPIParameters, AlterRoleAPIParameters
from middleware.auth import require_roles
logger = logging.getLogger(__name__)
users_router = APIRouter(prefix="/users", tags=["users"])
UserInterfaceInstance = UserInterface()


# 用户注册接口
@users_router.post("/register")
async def register_user(
        params: UserTokenAPIParameters
) -> JSONResponse:
    try:
        async with AsyncDatabaseManagerInstance.get_session() as session:
            # 检查用户是否已存在
            if await UserInterfaceInstance.get_user_by_username(session, params.username):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "code": 1,
                        "msg": "Username already exists.",
                        "data": None
                    }
                )
            # 创建新用户
            hashed_password = get_password_hash(params.password)
            new_user = await UserInterfaceInstance.create_user(session, params.username, hashed_password, UserRoleType.USER)
            # 使用序列化器将用户对象转换为字典
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "code": 0,
                    "msg": "User registered successfully.",
                    "data": {
                        "user_id": new_user.user_uuid,
                        "nickname": new_user.nickname,
                        "role": new_user.role.value,
                        "create_time": new_user.create_time,
                        "update_time": new_user.update_time
                    }
                }
            )
    except Exception as e:
        error_stack = traceback.format_exc()
        logger.error(error_stack)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": 1,
                "msg": str(e),
                "data": None
            }
        )

@users_router.post("/login")
async def register_user(
        params: UserTokenAPIParameters
) -> JSONResponse:
    try:
        async with AsyncDatabaseManagerInstance.get_session() as session:
            user = await UserInterfaceInstance.get_user_by_username(session, params.username)
            if not user or not verify_password(params.password, user.password):
                return JSONResponse(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            content={
                                "code": 1,
                                "msg": "Incorrect username or password",
                                "data": None
                            }
                        )
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"username": user.nickname, "useruuid": user.user_uuid, "role": user.role.value}, expires_delta=access_token_expires
            )
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "code": 0,
                    "msg": "User login successfully.",
                    "data": {"access_token": access_token, "token_type": "bearer", "user_id": user.user_uuid}
                },
                headers= {"Authorization": "Bearer "+access_token}
            )
    except Exception as e:
        error_stack = traceback.format_exc()
        logger.error(error_stack)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": 1,
                "msg": str(e),
                "data": None
            }
        )
#
@users_router.delete("/{user_id}")
@require_roles(UserRoleType.ADMIN)
async def delete_user(request: Request, user_id: str) -> JSONResponse:
    """用户管理接口：删除用户"""
    try:
        async with AsyncDatabaseManagerInstance.get_session() as session:
            await UserInterfaceInstance.delete_user(session, user_id)
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "msg": "User deleted successfully.",
                    "data": None
                }
            )
    except Exception as e:
        error_stack = traceback.format_exc()
        logger.error(error_stack)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": 1,
                "msg": str(e),
                "data": None
            }
        )

# 用户管理接口：更新用户权限
@users_router.post("/alter_role")
@require_roles(UserRoleType.ADMIN)
async def update_user_role(
        request: Request,
        params: AlterRoleAPIParameters) -> JSONResponse:
    try:
        async with AsyncDatabaseManagerInstance.get_session() as session:
            # 通过 int 数值获取对应的 UserRoleType 枚举实例
            role_enum = UserRoleType(params.role)
            await UserInterfaceInstance.update_user_role(session, params.user_id, role_enum)
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "msg": "User role updated successfully.",
                    "data": None
                }
            )
    except Exception as e:
        error_stack = traceback.format_exc()
        logger.error(error_stack)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": 1,
                "msg": str(e),
                "data": None
            }
        )