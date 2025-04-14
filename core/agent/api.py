import asyncio
import traceback
import uuid

import aiohttp
from fastapi import (
    FastAPI, BackgroundTasks, APIRouter
)
import logging
from starlette import status
from starlette.responses import JSONResponse, StreamingResponse
from core.agent.request_agent_model import CreateAgentAPIParameters, UpdateAgentAPIParameters, AgentChatAPIParameters

logger = logging.getLogger(__name__)
agent_router = APIRouter(prefix="/agent", tags=["agents"])

@agent_router.post("/add_provider")
async def add_provider(
        params: CreateAgentAPIParameters
) -> JSONResponse:
    try:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "code": 0,
                "msg": "Creating the agent succeeds.",
                "data": ""
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
@agent_router.post("/update_provider")
async def add_provider(
        params: CreateAgentAPIParameters
) -> JSONResponse:
    try:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "code": 0,
                "msg": "Creating the agent succeeds.",
                "data": ""
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
@agent_router.post("/delete_provider")
async def delete_provider(
        params: CreateAgentAPIParameters
) -> JSONResponse:
    try:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "code": 0,
                "msg": "Creating the agent succeeds.",
                "data": ""
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

@agent_router.post("/search_provider")
async def delete_provider(
        params: CreateAgentAPIParameters
) -> JSONResponse:
    try:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "code": 0,
                "msg": "Creating the agent succeeds.",
                "data": ""
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

@agent_router.post("/create")
async def agent_create(
        params: CreateAgentAPIParameters
) -> JSONResponse:
    try:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "code": 0,
                "msg": "Creating the agent succeeds.",
                "data": ""
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

@agent_router.post("/update")
async def agent_update(
        params: UpdateAgentAPIParameters
) -> JSONResponse:
    try:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "code": 0,
                "msg": "Creating the agent succeeds.",
                "data": ""
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

@agent_router.post("/chat")
async def agent_update(
        params: AgentChatAPIParameters
) -> JSONResponse:
    try:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "code": 0,
                "msg": "Creating the agent succeeds.",
                "data": ""
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