import datetime
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
from core.users.request_agent_model import UserRegisterAPIParameters, AlterRoleAPIParameters
logger = logging.getLogger(__name__)
users_router = APIRouter(prefix="/users", tags=["users"])
UserInterfaceInstance = UserInterface()


# 用户注册接口
@users_router.post("/register")
async def register_user(
        params: UserRegisterAPIParameters
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
            _, hashed = BcryptSecurity.hash_password(params.password)
            new_user = await UserInterfaceInstance.create_user(session, params.username, hashed.decode('utf-8'), UserRoleType.USER)
            # 使用序列化器将用户对象转换为字典
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "code": 0,
                    "msg": "User registered successfully.",
                    "data": {
                        "user_id": new_user.id,
                        "nickname": new_user.nickname,
                        "role": new_user.role.value,
                        "create_time": new_user.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "update_time": new_user.update_time.strftime("%Y-%m-%d %H:%M:%S")
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

# 用户管理接口：删除用户
@users_router.delete("/{user_id}")
async def delete_user(user_id: str) -> JSONResponse:
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
async def update_user_role(params: AlterRoleAPIParameters) -> JSONResponse:
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