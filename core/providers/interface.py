import uuid
from typing import Optional, List, Any, Coroutine, Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.model import ProviderModel


class ProviderInterface:
    @staticmethod
    async def add_base_provider(session: AsyncSession, **kwargs) -> Optional[ProviderModel]:
        """增加基础供应商"""
        new_provider = ProviderModel(
            **kwargs
        )
        session.add(new_provider)
        await session.commit()
        await session.refresh(new_provider)
        return new_provider

    @staticmethod
    async def update_base_provider(session: AsyncSession, provider_id: str, name: str = None, description: str = None, icon: str = None) -> Optional[ProviderModel]:
        """修改基础供应商信息"""
        result = await session.execute(
            select(ProviderModel).where(ProviderModel.id == provider_id)
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
    async def delete_base_provider(session: AsyncSession, provider_id: str) -> Optional[ProviderModel]:
        """删除基础供应商信息"""
        result = await session.execute(
            select(ProviderModel).where(ProviderModel.id == provider_id)
        )
        provider = result.scalars().first()
        if provider:
            await session.delete(provider)
            await session.commit()
        return provider

    @staticmethod
    async def get_all_providers(session, page: int, page_size: int):
        """
        分页获取所有供应商
        :param session: 数据库会话
        :param page: 当前页码
        :param page_size: 每页大小
        :return: 供应商列表和总数
        """
        offset = (page - 1) * page_size
        query = select(ProviderModel).offset(offset).limit(page_size)
        count_query = select(func.count()).select_from(ProviderModel)
        providers = await session.execute(query)
        total = await session.scalar(count_query)
        return providers.scalars().all(), total

    @staticmethod
    async def get_base_providers_by_uuids(session: AsyncSession, id_list: List[str]) -> Sequence[ProviderModel]:
        """根据uuid列表获取基础供应商信息"""
        result = await session.execute(
            select(ProviderModel).where(ProviderModel.id.in_(id_list))
        )
        return result.scalars().all()
