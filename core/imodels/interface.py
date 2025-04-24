import uuid
from typing import Optional, List, Any, Coroutine, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.model import ModelManagementModel


class ModelInterface:
    @staticmethod
    async def add_base_model(session: AsyncSession, **kwargs) -> Optional[ModelManagementModel]:
        """增加模型"""
        new_model = ModelManagementModel(
            **kwargs
        )
        session.add(new_model)
        await session.commit()
        await session.refresh(new_model)
        return new_model

    @staticmethod
    async def update_base_model(session: AsyncSession, model_id: str, user_id:str,
                                name: str = None, description: str = None, icon: str = None, _type: str = None, config: Any = None) -> Optional[ModelManagementModel]:
        """修改模型信息"""
        result = await session.execute(
            select(ModelManagementModel).where(ModelManagementModel.id == model_id, ModelManagementModel.user_id == user_id)
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
            if _type:
                _model.type = _type
            await session.commit()
            await session.refresh(_model)
        else:
            raise ModuleNotFoundError("未查找到相关的实例")
        return _model

    @staticmethod
    async def delete_base_model(session: AsyncSession, model_id: str, user_id:str,) -> Optional[ModelManagementModel]:
        """删除基础供应商信息"""
        result = await session.execute(
            select(ModelManagementModel).where(ModelManagementModel.id == model_id, ModelManagementModel.user_id == user_id)
        )
        provider = result.scalars().first()
        if provider:
            await session.delete(provider)
            await session.commit()
        else:
            raise ModuleNotFoundError("未查找到相关的实例")
        return provider


