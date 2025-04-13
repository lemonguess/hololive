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
from core.live.request_live_model import CreateLiveAppAPIParameters
from tools.liplsreal import LipLsReal
from aiortc import RTCPeerConnection, RTCSessionDescription

from tools.webrtc import HumanPlayer
from utils.sse import EventSourceResponse
from utils import Opt
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
async def post(url, data):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                return await response.text()
    except aiohttp.ClientError as e:
        print(f'Error: {e}')

async def clean_up(**kwargs):
    pass

async def _run(push_url,nerfreal):
    # nerfreal = await asyncio.get_event_loop().run_in_executor(None, build_nerfreal,sessionid)
    # nerfreals[sessionid] = nerfreal

    pc = RTCPeerConnection()

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logger.info("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()

    player = HumanPlayer(nerfreal)
    audio_sender = pc.addTrack(player.audio)
    video_sender = pc.addTrack(player.video)

    await pc.setLocalDescription(await pc.createOffer())
    answer = await post(push_url,pc.localDescription.sdp)
    await pc.setRemoteDescription(RTCSessionDescription(sdp=answer,type='answer'))
    return pc
@live_router.get("/sse")
async def sse(params: CreateLiveAppAPIParameters):
    try:
        # 建立消息队列
        event_queue = asyncio.Queue()
        # 创建数字人实例
        opt = Opt()
        from tools.liplsreal import load_model,load_avatar,warm_up
        print(opt)
        session_id = uuid.uuid4().hex
        model = load_model("./source//models/checkpoint_step000562000.pth")
        avatar = load_avatar("wav2lip_avatar384")
        nerfreal = LipLsReal(opt, model, avatar)
        push_url = f"http://146.56.226.252:1985/rtc/v1/whip/?app=live&stream={session_id}"
        pc = await _run(push_url, nerfreal)
        async def event_generator():
            while True:
                event = await event_queue.get()
                yield f"data: {event}\n\n"
                await asyncio.sleep(0.1)
        return EventSourceResponse(event_generator(), media_type="text/event-stream")
    except asyncio.CancelledError:
            # 处理断开连接
        print("Client disconnected.")
        await clean_up()
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

@live_router.get("/webrtc")
async def sse(params: CreateLiveAppAPIParameters) -> EventSourceResponse:
    async def event_generator():
        res_str = "七夕情人节即将来临，我们为您准备了精美的鲜花和美味的蛋糕"
        for i in res_str:
            yield {
                "event": "message",
                "retry": 15000,
                "data": i
            }
            await asyncio.sleep(0.1)
    return EventSourceResponse(event_generator(), media_type="text/event-stream")