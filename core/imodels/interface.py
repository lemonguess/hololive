import uuid
from typing import Optional, List, Any, Coroutine, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.model import ModelManagementModel


class ModelInterface:
    @staticmethod
    async def add_base_model(session: AsyncSession, **kwargs) -> Optional[ModelManagementModel]:
        """增加基础供应商"""
        new_model = ModelManagementModel(
            **kwargs
        )
        session.add(new_model)
        await session.commit()
        await session.refresh(new_model)
        return new_model

    @staticmethod
    async def update_base_model(session: AsyncSession, imodel_uuid: str, user_uuid:str,
                                name: str = None, description: str = None, icon: str = None, config: Any = None) -> Optional[ModelManagementModel]:
        """修改基础供应商信息"""
        result = await session.execute(
            select(ModelManagementModel).where(ModelManagementModel.imodel_uuid == imodel_uuid, ModelManagementModel.user_uuid == user_uuid)
        )
        _model = result.scalars().first()
        if _model:
            if name:
                _model.name = name
            if description:
                _model.description = description
            if icon:
                _model.icon = icon
            if config:
                _model.config = config
            await session.commit()
            await session.refresh(_model)
        else:
            raise ModuleNotFoundError("未查找到相关的实例")
        return _model

    @staticmethod
    async def delete_base_model(session: AsyncSession, imodel_uuid: str, user_uuid:str,) -> Optional[ModelManagementModel]:
        """删除基础供应商信息"""
        result = await session.execute(
            select(ModelManagementModel).where(ModelManagementModel.imodel_uuid == imodel_uuid, ModelManagementModel.user_uuid == user_uuid)
        )
        provider = result.scalars().first()
        if provider:
            await session.delete(provider)
            await session.commit()
        else:
            raise ModuleNotFoundError("未查找到相关的实例")
        return provider


