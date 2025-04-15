import asyncio

from utils.response_util import ResponseUtil
# from core.live.api import live_router
from core.agent.api import agent_router
from core.users.api import users_router
from tasks.startup_tasks import init_database, init_admin_user, init_default_provider
from utils.log_util import LOGGING_CONF, Logger
import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette import status
from contextlib import asynccontextmanager
# 日志配置
logger = Logger().get_logger()



@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup_event")
    await init_database()  # 库表初始化
    await asyncio.gather(
        await init_admin_user(),  # 系统启动时初始化管理员账号
        await init_default_provider() # 初始化默认模型供应商
    )
    yield  # 启动完成
    logger.info("shutdown_event")

app = FastAPI(lifespan=lifespan)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    # 自定义错误返回格式
    return ResponseUtil.error(
        message='参数校验错误',
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )
# app.include_router(live_router)
app.include_router(agent_router)
app.include_router(users_router)

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=6018,
        reload=True
    )