import asyncio
import traceback
from fastapi import (
    FastAPI, BackgroundTasks, APIRouter
)
import logging
from starlette import status
from starlette.responses import JSONResponse, StreamingResponse
from core.live.request_live_model import CreateLiveAppAPIParameters
logger = logging.getLogger(__name__)
live_router = APIRouter(prefix="/live", tags=["agents"])

@live_router.post("/create")
async def create_agent(
        params: CreateLiveAppAPIParameters
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
@live_router.get("/sse")
async def sse() -> StreamingResponse:
    async def stream():
        while True:
            try:
                # 发送事件
                yield f"data: Hello, world!\n\n"
                await asyncio.sleep(1)  # 每秒发送一次事件
            except asyncio.CancelledError:
                # 处理断开连接
                logger.info("Client disconnected.")
                # 在这里添加断开后的操作
                break

    return StreamingResponse(stream(), media_type="text/event-stream")