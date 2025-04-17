from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from sqlalchemy import update
import uuid
from models.enums import UserRoleType
from models.model import UsersModel
class UserInterface:
    @staticmethod
    async def get_user_by_username(session: AsyncSession, username: str) -> Optional[UsersModel]:
        """通过用户名获取用户信息（含软删除校验）"""
        result = await session.execute(
            select(UsersModel)
            .filter(UsersModel.nickname == username,
                    UsersModel.is_deleted == 0)
        )
        return result.scalars().first()

    @staticmethod
    async def get_user_by_email(session: AsyncSession, email: str) -> Optional[UsersModel]:
        """通过邮箱获取用户信息（含软删除校验）"""
        result = await session.execute(
            select(UsersModel)
            .filter(UsersModel.email == email,
                    UsersModel.is_deleted == 0)
        )
        return result.scalars().first()

    @staticmethod
    async def create_user(session: AsyncSession,
                        username: str,
                        password: str,
                        role: UserRoleType,
                        user_uuid: str = None) -> UsersModel:
        """创建新用户（自动事务管理）"""
        new_user = UsersModel(
            user_uuid=user_uuid if user_uuid else uuid.uuid4().hex,
            nickname=username,
            password=password,
            role=role,
            create_time=datetime.utcnow(),
            update_time=datetime.utcnow()
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user

    @staticmethod
    async def delete_user(session: AsyncSession, user_id: str) -> None:
        """原子化软删除操作"""
        await session.execute(
            update(UsersModel)
            .where(UsersModel.user_uuid == user_id)
            .values(
                is_deleted=1,
                update_time=datetime.utcnow()
            )
        )
        await session.commit()

    @staticmethod
    async def update_user_role(session: AsyncSession,
                             user_id: str,
                             role: UserRoleType) -> None:
        """角色更新（使用ORM表达式）"""
        await session.execute(
            update(UsersModel)
            .where(UsersModel.user_uuid == user_id)
            .values(
                role=role,
                update_time=datetime.utcnow()
            )
        )
        await session.commit()

    @staticmethod
    async def disable_user(session: AsyncSession, user_id: int) -> None:
        """禁用用户（批量更新优化）"""
        await session.execute(
            update(UsersModel)
            .where(UsersModel.id == user_id)
            .values(
                is_deleted=1,
                update_time=datetime.utcnow()
            )
        )
        await session.commit()