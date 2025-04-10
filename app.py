import os
import time
from pathlib import Path
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette import status
from utils.response_util import ResponseUtil
from core.live.api import live_router
app = FastAPI()
# 日志配置
logs_dir = Path(__file__).parent / "logs"
os.makedirs(logs_dir, exist_ok=True)  # 自动创建目录
log_config = uvicorn.config.LOGGING_CONFIG
log_config["handlers"]["access"]["filename"] = str(logs_dir / "access-{}.log".format(time.strftime("%Y-%m-%d")))
log_config["handlers"]["error"]["filename"] = str(logs_dir / "error-{}.log".format(time.strftime("%Y-%m-%d")))  # 新增错误日志
log_config["formatters"]["default"]["fmt"] = "%(asctime)s - [%(levelname)s] %(message)s"
log_config["formatters"]["access"]["fmt"] = '%(asctime)s - %(client_addr)s - "%(request_line)s" %(status_code)s'
log_config["handlers"]["access"]["class"] = "logging.handlers.TimedRotatingFileHandler"
log_config["handlers"]["access"]["when"] = "midnight"  # 每日滚动
log_config["handlers"]["access"]["backupCount"] = 7    # 保留7天日志
logger = logging.getLogger(__name__)
app.include_router(live_router)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    # 自定义错误返回格式
    return ResponseUtil.error(
        message='参数校验错误',
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )
app = FastAPI()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=6018,
        log_config=log_config,  # 注入配置
        reload=True
    )