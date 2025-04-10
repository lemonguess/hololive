# celery_app.py
from celery import Celery
from config import app_config

celery_app = Celery(
    "worker",
    broker=f"redis://{app_config.redis_config.host}:{app_config.redis_config.port}/{app_config.celery_config.celery_broker_db}",    # 消息队列地址
    backend=f"redis://{app_config.redis_config.host}:{app_config.redis_config.port}/{app_config.celery_config.celery_backend_db}",   # 结果存储
    include=["app.tasks"]                # 自动发现任务模块
)
celery_app.conf.update(
    task_track_started=True,              # 跟踪任务启动状态
    result_expires=app_config.celery_config.result_expires
)