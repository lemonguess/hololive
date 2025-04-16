import asyncio
from fastapi import FastAPI
from starlette import status
from contextlib import asynccontextmanager
from utils.response_util import ResponseUtil
from core.agents.api import agent_router
from core.users.api import users_router
from core.providers.api import provider_router
from core.imodels.api import imodel_router
from tasks.startup_tasks import init_database, init_admin_user, init_default_provider
from utils.log_util import LOGGING_CONF, Logger
import uvicorn
from middleware.jwt_middleware import JWTMiddleware
from middleware.validation_middleware import ValidationMiddleware
# 日志配置
logger = Logger().get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup_event")
    await init_database()  # 库表初始化
    await asyncio.gather(
        init_admin_user(),  # 系统启动时初始化管理员账号
        init_default_provider() # 初始化默认模型供应商
    )
    yield  # 启动完成
    logger.info("shutdown_event")

app = FastAPI(lifespan=lifespan)

# 添加 JWT 中间件
# app.add_middleware(JWTMiddleware)
# 添加参数校验中间件
# app.add_middleware(ValidationMiddleware)


app.include_router(agent_router)
app.include_router(users_router)
app.include_router(provider_router)
app.include_router(imodel_router)

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=6018,
        reload=True
    )
