import uuid
from typing import Optional, List, Any, Coroutine, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.model import FileInfo
from utils.db_interface import DBInterface


class FileInterface(DBInterface):
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
    async def update(session: AsyncSession, *args, **kwargs) -> Optional[FileInfo]:
        file_id = kwargs["file_id"]
        file_name = kwargs["file_name"]
        obj_name = kwargs["obj_name"]
        result = await session.execute(
            select(FileInfo).where(FileInfo.id == file_id)
        )
        _model = result.scalars().first()
        if _model:
            _model.file_name = file_name
            _model.obj_name = obj_name
            await session.commit()
            await session.refresh(_model)
        else:
            raise ModuleNotFoundError("未查找到相关的实例")
        return _model
    @staticmethod
    async def list(session: AsyncSession, *args, **kwargs):
        """批量查询"""
        file_id_list = kwargs["file_id_list"]
        result = await session.execute(
            select(FileInfo).where(FileInfo.id.in_(file_id_list))
        )
        models = result.scalars().all()
        return models
    @staticmethod
    async def delete(session: AsyncSession, *args, **kwargs) -> Optional[FileInfo]:
        model_id = kwargs["model_id"]
        user_id = kwargs["user_id"]
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


