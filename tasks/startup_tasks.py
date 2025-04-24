from sqlalchemy import select

from core.users.api import UserInterfaceInstance
from models.model import ProviderModel
from utils import AsyncDatabaseManagerInstance
from middleware.auth import get_password_hash
# from models.model import Role  # 导入Role模型
from models.enums import UserRoleType
from models.base import Base
from config import app_config
import logging
import json
from pathlib import Path
logger = logging.getLogger(__name__)
async def init_database():
    """库表初始化"""
    await AsyncDatabaseManagerInstance.create_tables(Base)

async def init_admin_user():
    admin_username = app_config.admin.admin_username
    admin_password = app_config.admin.admin_password
    hashed = get_password_hash(admin_password)
    async with AsyncDatabaseManagerInstance.get_session() as session:
        # 检查管理员是否存在
        admin_user = await UserInterfaceInstance.get_user_by_username(session, admin_username)
        if not admin_user:
            await UserInterfaceInstance.create_user(
                session,
                username=admin_username,
                password=hashed,
                role=UserRoleType.ADMIN,
                user_id="571998a36f4b4ffeb2aaccc752d52bc4"
            )
            logger.info("Admin user initialized.")
    public_username = app_config.admin.public_username
    public_password = app_config.admin.public_password
    hashed = get_password_hash(public_password)
    async with AsyncDatabaseManagerInstance.get_session() as session:
        # 检查公共账号是否存在
        admin_user = await UserInterfaceInstance.get_user_by_username(session, public_username)
        if not admin_user:
            await UserInterfaceInstance.create_user(
                session,
                username=public_username,
                password=hashed,
                role=UserRoleType.ADMIN,
                user_id="aa4690c854b8462f93ef0f5bb3e3b921"
            )
            logger.info("Public user initialized.")

async def init_default_provider():
    """初始化默认供应商数据"""
    # 异步读取默认供应商配置文件
    config_path = 'config/default_providers.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        providers = json.load(f)
    # 将数据写入数据库
    async with AsyncDatabaseManagerInstance.get_session() as session:
        for provider in providers:
            existing_provider = await session.execute(
                select(ProviderModel).where(ProviderModel.id==provider['provider_uuid'])
            )
            if not existing_provider.first():
                new_provider = ProviderModel(
                    id=provider['provider_uuid'],
                    icon=provider.get('icon'),
                    name=provider['name'],
                    name_zh=provider['name_zh'] if provider.get("name_zh") else provider['name'],
                    description=provider.get('description')
                )
                session.add(new_provider)
        await session.commit()


# def init_user_roles():
#     """初始化用户角色表"""
#     async with AsyncDatabaseManagerInstance.get_session() as session:
#         # 检查是否已经存在角色数据
#         if session.query(Role).count() == 0:
#             # 插入默认角色
#             for role in UserRoleType:
#                 session.add(Role(id=role.value, name=role.name))
#             session.commit()