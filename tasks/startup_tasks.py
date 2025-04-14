from core.users.api import UserInterfaceInstance
from utils import AsyncDatabaseManagerInstance
from utils.encrypt_util import BcryptSecurity
from models.enums import UserRoleType
from models.base import Base
from config import app_config
import logging
logger = logging.getLogger(__name__)
async def init_database():
    """库表初始化"""
    await AsyncDatabaseManagerInstance.create_tables(Base)
#
async def init_admin_user():
    admin_username = app_config.admin.admin_username
    admin_password = app_config.admin.admin_username
    _, hashed = BcryptSecurity.hash_password(admin_password)
    async with AsyncDatabaseManagerInstance.get_session() as session:
        # 检查管理员是否存在
        admin_user = await UserInterfaceInstance.get_user_by_username(session, admin_username)
        if not admin_user:
            # 创建管理员（移除多余的manager参数）
            await UserInterfaceInstance.create_user(
                session,
                username=admin_username,
                password=hashed,
                role=UserRoleType.ADMIN
            )
            logger.info("Admin user initialized.")
