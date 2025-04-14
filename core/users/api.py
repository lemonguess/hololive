import traceback

from fastapi import (
    APIRouter
)
import logging
from starlette import status
from starlette.responses import JSONResponse

from core.users.interface import UserInterface
from models.enums import UserRoleType
from utils import AsyncDatabaseManagerInstance
from utils.encrypt_util import BcryptSecurity
logger = logging.getLogger(__name__)
users_router = APIRouter(prefix="/users", tags=["users"])
UserInterfaceInstance = UserInterface()


# 用户注册接口
@users_router.post("/register")
async def register_user(
        username: str,
        password: str
) -> JSONResponse:
    try:
        async with AsyncDatabaseManagerInstance.get_session() as session:
            # 检查用户是否已存在
            if await UserInterfaceInstance.get_user_by_username(session, username):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "code": 1,
                        "msg": "Username already exists.",
                        "data": None
                    }
                )
            # 创建新用户
            _, hashed = BcryptSecurity.hash_password(password)
            await UserInterfaceInstance.create_user(session, username, hashed, UserRoleType.USER)
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "code": 0,
                    "msg": "User registered successfully.",
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

# 用户管理接口：删除用户
@users_router.delete("/users/{user_id}")
async def delete_user(user_id: int) -> JSONResponse:
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
@users_router.put("/users/{user_id}/role")
async def update_user_role(user_id: int, role: UserRoleType) -> JSONResponse:
    try:
        async with AsyncDatabaseManagerInstance.get_session() as session:
            await UserInterfaceInstance.update_user_role(session, user_id, role)
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

# 用户管理接口：禁用用户
@users_router.put("/users/{user_id}/disable")
async def disable_user(user_id: int) -> JSONResponse:
    try:
        async with AsyncDatabaseManagerInstance.get_session() as session:
            await UserInterfaceInstance.disable_user(session, user_id)
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "msg": "User disabled successfully.",
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