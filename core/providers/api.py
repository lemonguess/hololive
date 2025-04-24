import traceback
import uuid

import sqlalchemy
from fastapi import (
    FastAPI, BackgroundTasks, APIRouter, Request
)
import logging
from starlette import status
from starlette.responses import JSONResponse
from core.providers.interface import ProviderInterface
from core.providers.schemas import *
from models.enums import UserRoleType
from utils import AsyncDatabaseManagerInstance
from utils import Serializer
from fastapi import Request
from middleware.auth import require_roles, get_current_user_uuid
logger = logging.getLogger(__name__)
provider_router = APIRouter(prefix="/provider", tags=["providers"])
@provider_router.post("/add_base_provider")
@require_roles(UserRoleType.ADMIN)
async def add_base_provider(
        request: Request,
        params: AddBaseProviderAPIParameters
) -> JSONResponse:
    try:
        async with AsyncDatabaseManagerInstance.get_session() as session:
            item = {
                "id": uuid.uuid4().hex,
                "icon": params.icon,
                "description": params.description,
                "name": params.name,
            }
            provider = await ProviderInterface.add_base_provider(
                session=session, **item
            )
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "code": 0,
                    "msg": "Base provider added successfully.",
                    "data": provider.id
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


@provider_router.post("/update_base_provider")
@require_roles(UserRoleType.ADMIN)
async def update_base_provider(
        request: Request,
        params: UpdateBaseProviderAPIParameters
) -> JSONResponse:
    try:
        async with AsyncDatabaseManagerInstance.get_session() as session:
            provider = await ProviderInterface.update_base_provider(
                session=session,
                provider_id=params.provider_id,
                name=params.name,
                description=params.description,
                icon=params.icon
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "msg": "Base provider updated successfully.",
                    "data": provider.id
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


@provider_router.post("/delete_base_provider")
@require_roles(UserRoleType.ADMIN)
async def delete_base_provider(
        request: Request,
        params: DeleteBaseProviderAPIParameters
) -> JSONResponse:
    try:
        async with AsyncDatabaseManagerInstance.get_session() as session:
            provider = await ProviderInterface.delete_base_provider(
                session=session,
                provider_id=params.provider_id
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "msg": "Base provider deleted successfully.",
                    "data": provider.id
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


@provider_router.post("/get_all_providers")
@require_roles(UserRoleType.ADMIN)
async def get_all_providers(
        request: Request,
        params: PaginationParameters
) -> JSONResponse:
    try:
        async with AsyncDatabaseManagerInstance.get_session() as session:
            providers, total = await ProviderInterface.get_all_providers(
                session=session,
                page=params.page,
                page_size=params.page_size
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "msg": "Providers fetched successfully.",
                    "data": {
                        "providers": [Serializer.serialize(provider) for provider in providers],
                        "total": total
                    }
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


@provider_router.post("/get_base_providers_by_uuids")
@require_roles(UserRoleType.FORBID)
async def get_base_providers_by_uuids(
        request: Request,
        params: SearchBaseProviderAPIParameters
) -> JSONResponse:
    try:
        async with AsyncDatabaseManagerInstance.get_session() as session:
            providers = await ProviderInterface.get_base_providers_by_uuids(
                session=session,
                id_list=params.id_list
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "msg": "Base providers fetched successfully.",
                    "data": [Serializer.serialize(provider) for provider in providers]
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




