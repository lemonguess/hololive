from core.imodels.interface import ModelInterface
from core.imodels.schemas import *
from middleware.auth import require_roles, get_current_user_uuid
from models.enums import UserRoleType, ModelType
from utils import AsyncDatabaseManagerInstance
from utils import Serializer
from utils.generalUtil import json_loads
import traceback
import uuid
import sqlalchemy
from fastapi import (
    FastAPI, BackgroundTasks, APIRouter, Request
)
import logging
from starlette import status
from starlette.responses import JSONResponse
logger = logging.getLogger(__name__)
imodel_router = APIRouter(prefix="/models", tags=["models"])
@imodel_router.post("/add_base_model")
@require_roles(UserRoleType.FORBID)
async def add_base_model(
        request: Request,
        params: AddBaseModelAPIParameters
) -> JSONResponse:
    """模型添加接口"""
    try:
        user_uuid = get_current_user_uuid(request)
        async with AsyncDatabaseManagerInstance.get_session() as session:
            item = {
                "user_provider_uuid": params.user_provider_uuid,
                "user_uuid": user_uuid,
                "imodel_uuid": uuid.uuid4().hex,
                "imodel_type": ModelType(params.imodel_type),  # 根据 params.imodel_type 获取 ModelType 实例
                "icon": params.icon,
                "description": params.description,
                "name": params.name,
                "config": json_loads(params.config)
            }
            _model = await ModelInterface.add_base_model(
                session=session, **item
            )
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "code": 0,
                    "msg": "Base model added successfully.",
                    "data": Serializer.serialize(_model)
                }
            )
    except sqlalchemy.exc.IntegrityError as e:
        error_stack = traceback.format_exc()
        logger.error(error_stack)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": 1,
                "msg": str(e.args),
                "data": None
            }
        )

@imodel_router.post("/update_base_provider")
@require_roles(UserRoleType.FORBID)
async def update_base_provider(
        request: Request,
        params: UpdateBaseModelAPIParameters
) -> JSONResponse:
    """模型修改接口"""
    try:
        user_uuid = get_current_user_uuid(request)
        async with AsyncDatabaseManagerInstance.get_session() as session:
            _model = await ModelInterface.update_base_model(
                session=session,
                imodel_uuid=params.imodel_uuid,
                user_uuid=user_uuid,
                name=params.name,
                description=params.description,
                icon=params.icon,
                config=json_loads(params.config)
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "msg": "Base model updated successfully.",
                    "data": Serializer.serialize(_model)
                }
            )
    except Exception as e:
        error_stack = traceback.format_exc()
        logger.error(error_stack)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": 1,
                "msg": str(e.args),
                "data": None
            }
        )

@imodel_router.delete("/delete_base_model")
@require_roles(UserRoleType.FORBID)
async def delete_base_model(
        request: Request,
        params: DeleteBaseModelAPIParameters
) -> JSONResponse:
    try:
        user_uuid = get_current_user_uuid(request)
        async with AsyncDatabaseManagerInstance.get_session() as session:
            provider = await ModelInterface.delete_base_model(
                session=session,
                imodel_uuid=params.imodel_uuid,
                user_uuid=user_uuid
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "msg": "Base model deleted successfully.",
                    "data": Serializer.serialize(provider)
                }
            )
    except Exception as e:
        error_stack = traceback.format_exc()
        logger.error(error_stack)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": 1,
                "msg": str(e),
                "data": None
            }
        )


