import traceback
import uuid

import sqlalchemy
from fastapi import (
    FastAPI, BackgroundTasks, APIRouter
)
import logging
from starlette import status
from starlette.responses import JSONResponse
from core.providers.interface import ProviderInterface
from core.providers.request_model import *
from sqlalchemy.ext.asyncio import AsyncSession
from utils import AsyncDatabaseManagerInstance
from utils import Serializer
logger = logging.getLogger(__name__)
provider_router = APIRouter(prefix="/provider", tags=["providers"])
@provider_router.post("/add_base_provider")
async def add_base_provider(
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
async def update_base_provider(
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
async def delete_base_provider(
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
async def add_user_provider(
        params: AddUserProviderAPIParameters
) -> JSONResponse:
    try:
        async with AsyncDatabaseManagerInstance.get_session() as session:
            user_provider = await ProviderInterface.add_user_provider(
                session=session,
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
async def update_user_provider(
        params: UpdateUserProviderAPIParameters
) -> JSONResponse:
    try:
        async with AsyncDatabaseManagerInstance.get_session() as session:
            user_provider = await ProviderInterface.update_user_provider(
                session=session,
                user_provider_uuid=params.user_provider_uuid,
                api_key=params.api_key,
                base_url=params.base_url
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
async def delete_user_provider(
        params: DeleteUserProviderAPIParameters
) -> JSONResponse:
    try:
        async with AsyncDatabaseManagerInstance.get_session() as session:
            await ProviderInterface.delete_user_provider(
                session=session,
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
async def get_base_providers_by_uuids(
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
async def get_user_providers_by_uuids(
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


