import asyncio
import traceback
import uuid

import aiohttp
from fastapi import (
    FastAPI, BackgroundTasks, APIRouter, Request
)
import logging
from starlette import status
from starlette.responses import JSONResponse
from core.agents.schemas import CreateAgentAPIParameters, UpdateAgentAPIParameters, AgentChatAPIParameters

logger = logging.getLogger(__name__)
agent_router = APIRouter(prefix="/agent", tags=["agents"])





@agent_router.post("/create")
async def agent_create(
        request: Request,
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
        request: Request,
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
        request: Request,
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
