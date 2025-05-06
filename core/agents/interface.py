from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.model import ModelManagementModel

class AgentInterface:
    @staticmethod
    async def add_base_provider(session: AsyncSession, provider_uuid: str, name: str, description: str = None, icon: str = None) -> Optional[BaseProviderModel]:
        """增加供应商"""
        new_provider = ModelManagementModel(
            provider_uuid=provider_uuid,
            name=name,
            description=description,
            icon=icon
        )
        session.add(new_provider)
        await session.commit()
        await session.refresh(new_provider)
        return new_provider

