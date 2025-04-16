import uuid
from typing import Optional, List, Any, Coroutine, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.model import BaseSupplierModel, UserSupplierModel


class ProviderInterface:
    @staticmethod
    async def add_base_provider(session: AsyncSession, **kwargs) -> Optional[BaseSupplierModel]:
        """增加基础供应商"""
        new_provider = BaseSupplierModel(
            **kwargs
        )
        session.add(new_provider)
        await session.commit()
        await session.refresh(new_provider)
        return new_provider

    @staticmethod
    async def update_base_provider(session: AsyncSession, provider_uuid: str, name: str = None, description: str = None, icon: str = None) -> Optional[BaseSupplierModel]:
        """修改基础供应商信息"""
        result = await session.execute(
            select(BaseSupplierModel).where(BaseSupplierModel.provider_uuid == provider_uuid)
        )
        provider = result.scalars().first()
        if provider:
            if name:
                provider.name = name
            if description:
                provider.description = description
            if icon:
                provider.icon = icon
            await session.commit()
            await session.refresh(provider)
        return provider

    @staticmethod
    async def delete_base_provider(session: AsyncSession, provider_uuid: str) -> Optional[BaseSupplierModel]:
        """删除基础供应商信息"""
        result = await session.execute(
            select(BaseSupplierModel).where(BaseSupplierModel.provider_uuid == provider_uuid)
        )
        provider = result.scalars().first()
        if provider:
            await session.delete(provider)
            await session.commit()
        return provider

    @staticmethod
    async def add_user_provider(session: AsyncSession, **kwargs) -> UserSupplierModel:
        """增加用户供应商信息"""
        new_user_provider = UserSupplierModel(
            user_provider_uuid=uuid.uuid4().hex,
            **kwargs
        )
        session.add(new_user_provider)
        await session.commit()
        await session.refresh(new_user_provider)
        return new_user_provider

    @staticmethod
    async def update_user_provider(session: AsyncSession, user_provider_uuid: str, api_key: str = None, base_url: str = None) -> Optional[UserSupplierModel]:
        """修改用户供应商信息"""
        result = await session.execute(
            select(UserSupplierModel).where(UserSupplierModel.user_provider_uuid == user_provider_uuid)
        )
        user_provider = result.scalars().first()
        if user_provider:
            if api_key:
                user_provider.api_key = api_key
            if base_url:
                user_provider.base_url = base_url
            await session.commit()
            await session.refresh(user_provider)
        return user_provider

    @staticmethod
    async def delete_user_provider(session: AsyncSession, user_provider_uuid: str) -> Optional[UserSupplierModel]:
        """删除用户供应商信息"""
        result = await session.execute(
            select(UserSupplierModel).where(UserSupplierModel.user_provider_uuid == user_provider_uuid)
        )
        user_provider = result.scalars().first()
        if user_provider:
            await session.delete(user_provider)
            await session.commit()
        return user_provider

    @staticmethod
    async def get_base_providers_by_uuids(session: AsyncSession, uuid_list: List[str]) -> Sequence[BaseSupplierModel]:
        """根据uuid列表获取基础供应商信息"""
        result = await session.execute(
            select(BaseSupplierModel).where(BaseSupplierModel.provider_uuid.in_(uuid_list))
        )
        return result.scalars().all()

    @staticmethod
    async def get_user_providers_by_uuids(session: AsyncSession, uuid_list: List[str]) -> Sequence[UserSupplierModel]:
        """根据uuid列表获取用户供应商信息"""
        result = await session.execute(
            select(UserSupplierModel).where(UserSupplierModel.user_provider_uuid.in_(uuid_list))
        )
        return result.scalars().all()
