from utils.async_database_manager import AsyncDatabaseManager
from utils.livetalking_options import Opt
from utils.serializer import Serializer
# from utils.milvus_conn import mlivus_client
from utils.minio_conn import MinioConnection


# def automatic_migration():
#     from database.milvus_orm import tables
#     for table in tables:
#         mlivus_client.create_collection(table.__table_name__, table)


# automatic_migration()
# minio客户端
minio_client = MinioConnection()
# 数字人配置项
opt = Opt()
# 连接池实例
AsyncDatabaseManagerInstance = AsyncDatabaseManager()