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
                "provider_uuid": uuid.uuid4().hex,
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
                    "data": provider.provider_uuid
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
                provider_uuid=params.provider_uuid,
                name=params.name,
                description=params.description,
                icon=params.icon
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "msg": "Base provider updated successfully.",
                    "data": provider.provider_uuid
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
                provider_uuid=params.provider_uuid
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "msg": "Base provider deleted successfully.",
                    "data": provider.provider_uuid
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


@provider_router.post("/add_user_provider")
@require_roles(UserRoleType.FORBID)
async def add_user_provider(
        request: Request,
        params: AddUserProviderAPIParameters
) -> JSONResponse:
    try:
        user_uuid = get_current_user_uuid(request)
        async with AsyncDatabaseManagerInstance.get_session() as session:
            user_provider = await ProviderInterface.add_user_provider(
                session=session,
                user_uuid=user_uuid,
                **params.__dict__
            )
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "code": 0,
                    "msg": "User provider added successfully.",
                    "data": user_provider.user_provider_uuid
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

@provider_router.post("/update_user_provider")
@require_roles(UserRoleType.FORBID)
async def update_user_provider(
        request: Request,
        params: UpdateUserProviderAPIParameters
) -> JSONResponse:
    try:
        user_uuid = get_current_user_uuid(request)
        async with AsyncDatabaseManagerInstance.get_session() as session:
            user_provider = await ProviderInterface.update_user_provider(
                session=session,
                user_provider_uuid=params.user_provider_uuid,
                api_key=params.api_key,
                base_url=params.base_url,
                user_uuid=user_uuid
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "msg": "User provider updated successfully.",
                    "data": user_provider.user_provider_uuid
                }
            )
    except sqlalchemy.exc.IntegrityError:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": 1,
                "msg": "修改信息重复",
                "data": None
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


@provider_router.delete("/delete_user_provider")
@require_roles(UserRoleType.FORBID)
async def delete_user_provider(
        request: Request,
        params: DeleteUserProviderAPIParameters
) -> JSONResponse:
    try:
        user_uuid = get_current_user_uuid(request)
        async with AsyncDatabaseManagerInstance.get_session() as session:
            await ProviderInterface.delete_user_provider(
                session=session,
                user_uuid=user_uuid,
                user_provider_uuid=params.user_provider_uuid
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "msg": "User provider deleted successfully.",
                    "data": "ok"
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


@provider_router.post("/get_base_providers_by_uuids")
@require_roles(UserRoleType.FORBID)
async def get_base_providers_by_uuids(
        request: Request,
        params: SearchUserProviderAPIParameters
) -> JSONResponse:
    try:
        async with AsyncDatabaseManagerInstance.get_session() as session:
            providers = await ProviderInterface.get_base_providers_by_uuids(
                session=session,
                uuid_list=params.uuid_list
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


@provider_router.post("/get_user_providers_by_uuids")
@require_roles(UserRoleType.FORBID)
async def get_user_providers_by_uuids(
        request: Request,
        params: SearchUserProviderAPIParameters
) -> JSONResponse:
    try:
        async with AsyncDatabaseManagerInstance.get_session() as session:
            providers = await ProviderInterface.get_user_providers_by_uuids(
                session=session,
                uuid_list=params.uuid_list
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "msg": "User providers fetched successfully.",
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


