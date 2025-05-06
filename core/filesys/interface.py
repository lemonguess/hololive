import uuid
from typing import Optional, List, Any, Coroutine, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.model import FileInfo


class FileInterface:
    @staticmethod
    async def add(session: AsyncSession, **kwargs) -> Optional[FileInfo]:
        """增加数据"""
        new_model = FileInfo(
            **kwargs
        )
        session.add(new_model)
        await session.commit()
        await session.refresh(new_model)
        return new_model

    @staticmethod
    async def update(session: AsyncSession, file_id: str, file_name:str,
                                ) -> Optional[FileInfo]:
        result = await session.execute(
            select(FileInfo).where(FileInfo.id == file_id)
        )
        _model = result.scalars().first()
        if _model:
            if file_name:
                _model.file_name = file_name
            await session.commit()
            await session.refresh(_model)
        else:
            raise ModuleNotFoundError("未查找到相关的实例")
        return _model
    @staticmethod
    async def list(session: AsyncSession, file_id_list:list,):
        """批量查询"""
        result = await session.execute(
            select(FileInfo).where(FileInfo.id.in_(file_id_list))
        )
        models = result.scalars().all()
        return models
    @staticmethod
    async def delete(session: AsyncSession, model_id: str, user_id:str,) -> Optional[FileInfo]:
        result = await session.execute(
            select(FileInfo).where(FileInfo.id == model_id, FileInfo.user_id == user_id)
        )
        provider = result.scalars().first()
        if provider:
            await session.delete(provider)
            await session.commit()
        else:
            raise ModuleNotFoundError("未查找到相关的实例")
        return provider


