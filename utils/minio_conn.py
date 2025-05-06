# coding: utf-8

from minio import Minio, S3Error
from io import BytesIO
from datetime import timedelta
import json
from minio.commonconfig import CopySource
from config.get_config import get_config_parser
import logging
logger = logging.getLogger(__name__)


class MinioConnection:
    def __init__(self):
        self.conf_mange = get_config_parser()
        self.client: Minio = None
        self.make_conn()

    def make_conn(self):
        self.client: Minio = Minio(
            endpoint=self.conf_mange.minio_config.endpoint,
            access_key=self.conf_mange.minio_config.access_key,
            secret_key=self.conf_mange.minio_config.secret_key,
            secure=False
        )

    def init_bucket_policy(self, bucket_name: str):
        """ 初始化桶策略-设置新桶永久分享策略 """
        bucket_policy = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Effect': 'Allow',
                    'Principal': {'AWS': ['*']},
                    'Action': ['s3:GetBucketLocation', 's3:ListBucket'],
                    'Resource': [f'arn:aws:s3:::{bucket_name}']
                },
                {
                    'Effect': 'Allow',
                    'Principal': {'AWS': ['*']},
                    'Action': ['s3:GetObject'],
                    'Resource': [f'arn:aws:s3:::{bucket_name}/*']
                }
            ]
        }
        self.client.set_bucket_policy(bucket_name=bucket_name, policy=json.dumps(bucket_policy))

    def __make_bucket(self, bucket_name: str):
        if self.client.bucket_exists(bucket_name):
            logger.info('Bucket already exists')
            return
        self.client.make_bucket(bucket_name)
        self.init_bucket_policy(bucket_name)
        logger.info('Bucket create successfully')

    def __list_bucket(self):
        return [bucket.name for bucket in self.client.list_buckets()]

    def put(self, bucket_name: str, file_name: str, data: BytesIO):
        for i in range(10):
            try:
                self.__make_bucket(bucket_name)
                length = data.getbuffer().nbytes
                if file_name.endswith('.svg'):
                    self.client.put_object(bucket_name, file_name, data, length, content_type="image/svg+xml")
                elif file_name.endswith('.js'):
                    self.client.put_object(bucket_name, file_name, data, length, content_type="application/javascript")
                elif file_name.endswith('.css'):
                    self.client.put_object(bucket_name, file_name, data, length, content_type="text/x-scss")
                else:
                    self.client.put_object(bucket_name, file_name, data, length)
                logger.info('put successfully')
                return True
            except Exception as e:
                logger.error("Minio server connect failed, Retry!")
                self.make_conn()
        return False

    def get(self, bucket_name: str, file_name: str):
        content = None
        for i in range(10):
            try:
                content = self.client.get_object(bucket_name, file_name)
                break
            except S3Error as se:
                logger.error("File not exist")
                return content
            except Exception as e:
                logger.error("Minio server connect failed, Retry!")
                self.make_conn()
        return content

    def get_file_url(self, bucket_name: str, file_name: str):
        for i in range(10):
            try:
                uri = self.client.presigned_get_object(bucket_name=bucket_name, object_name=file_name, expires=timedelta(days=7))
                return uri
            except Exception as e:
                logger.error("Minio server connect failed, Retry!")
                self.make_conn()
        return None

    def delete(self, bucket_name: str, file_name: str):
        for i in range(10):
            try:
                self.client.remove_object(bucket_name=bucket_name, object_name=file_name)
                return True
            except Exception as e:
                logger.error("Minio server connect failed, Retry!")
                self.make_conn()
        return False

    def rename_file(self, bucket_name: str, object_name: str, new_name: str):
        for i in range(10):
            try:
                self.client.copy_object(bucket_name, new_name, CopySource(bucket_name, object_name))
                self.client.remove_object(bucket_name, object_name)
                return True
            except Exception as e:
                logger.error("Minio server connect failed, Retry!")
                self.make_conn()
        return False



if __name__ == '__main__':
    minios = MinioConnection()
    # minios.put("aaa", "README.md", BytesIO(b"hello world"))
    content = minios.get("aaa", "README.md")
    # uri = minios.remove_user("aaa")
    print(content)
