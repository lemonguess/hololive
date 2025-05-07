# coding: utf-8
import json
import traceback
from typing import List, Dict
import uuid

from pymilvus import DataType, MilvusClient


from config.get_config import get_config_parser
import logging
logger = logging.getLogger(__name__)


class MilvusConn:
    def __init__(self):
        self.milvus_client: MilvusClient
        self.collection = None
        self.conf_manage = get_config_parser()
        self.__conn()
        # self.create_collection()

    def __conn(self):
        self.milvus_client = MilvusClient(uri=self.conf_manage.milvus_config.milvus_uri,
                                          user=self.conf_manage.milvus_config.milvus_user,
                                          password=self.conf_manage.milvus_config.milvus_password)
        logger.info("milvus connection established!")

    def create_schema(self):
        schema = self.milvus_client.create_schema(
            auto_id=True,
            enable_dynamic_field=True,
        )
        return schema

    def __check_schema(self, value):
        instance_attrs = {k: v for k, v in value.__dict__.items()}
        if value.datatype == DataType.INT64 and value.filed_name == "id":
            need_filed = ["field_name", "datatype", "is_primary", "auto_id"]
            for k, v in instance_attrs.items():
                if v is None and k in need_filed:
                    return f"{k} is required"
        elif value.datatype == DataType.VARCHAR:
            need_filed = ["field_name", "datatype", "is_primary", "max_length"]
            for k, v in instance_attrs.items():
                if v is None and k in need_filed:
                    return f"{k} is required"
        elif value.datatype == DataType.FLOAT_VECTOR:
            need_filed = ["field_name", "datatype", "is_primary", "dim"]
            for k, v in instance_attrs.items():
                if v is None and k in need_filed:
                    return f"{k} is required"
        elif value.datatype == DataType.INT64:
            need_filed = ["field_name", "datatype", "is_primary"]
            for k, v in instance_attrs.items():
                if v is None and k in need_filed:
                    return f"{k} is required"
        return "Done"

    def add_field(self, schema, filed):
        class_attrs = {k: v for k, v in filed.__dict__.items() if not k.startswith('__')}
        for key, value in class_attrs.items():
            check_value = self.__check_schema(value)
            if check_value != "Done":
                return check_value
            if value.datatype == DataType.INT64 and value.filed_name == "id":
                schema.add_field(field_name=value.filed_name, datatype=value.datatype, is_primary=value.is_primary,
                                 auto_id=value.auto_id)
            elif value.datatype == DataType.VARCHAR:
                schema.add_field(field_name=value.filed_name, datatype=value.datatype, is_primary=value.is_primary,
                                 max_length=value.max_length)
            elif value.datatype == DataType.INT64:
                schema.add_field(field_name=value.filed_name, datatype=value.datatype, is_primary=value.is_primary)
            elif value.datatype == DataType.FLOAT_VECTOR:
                schema.add_field(field_name=value.filed_name, datatype=value.datatype, dim=value.dim)
        return "Done"

    def create_index(self):
        index_params = self.milvus_client.prepare_index_params()
        index_params.add_index(
            field_name="embedding",
            index_type="IVF_FLAT",
            metric_type="IP",
            params={"nlist": 1024}
        )
        return index_params

    def create_collection(self, collection_name: str, filed):
        if self.milvus_client.has_collection(collection_name):
            # print(f"Collection '{self.collection_name}' already exists.")
            logger.info(f"Collection '{collection_name}' already exists.")
            return
        schema = self.create_schema()
        af = self.add_field(schema, filed)
        if af != "Done":
            raise Exception("Collection creation failed.")
        index_params = self.create_index()
        res = self.milvus_client.create_collection(
            collection_name=collection_name,
            schema=schema,
            index_params=index_params
        )
        # print(res)
        logger.info(res)

    def insert(self, data_in: list, collection_name: str, is_add: bool = False):
        try:
            if len(data_in) == 0:
                return False
            if not is_add:
                res = self.query(file_uuid=[data_in[0]['document_id']], collection_name=collection_name)
                if res[data_in[0]['document_id']]:
                    self.delete(document_id=data_in[0]['document_id'], collection_name=collection_name)

            self.milvus_client.insert(data=data_in, collection_name=collection_name)
            logger.info(f"Inserted records into {collection_name}")
            return True
        except Exception as e:
            logger.error("insert - " + str(e))
            return False

    def get_state(self, document_id: str, state: int, collection_name: str, output_fields: List, ):
        try:
            expr = f"document_id == '{document_id}' && state  == {state}"
            result = self.milvus_client.query(
                collection_name=collection_name,
                filter=expr,
                output_fields=output_fields,
            )

            result = sorted(result, key=lambda x: x['content_num'])
            logger.info(f"query_content的结果为: {result}")
            return result
        except Exception as e:
            logger.error("insert - " + str(e))
            return []

    def search(self, query_vectors, file_uuid, collection_name, top_k=5, threshold=0.5):
        try:
            load_ret = self.milvus_client.get_load_state(collection_name=collection_name)
            if load_ret['state'].name == 'NotLoad':
                self.milvus_client.load_collection(collection_name=collection_name)
            search_params = {
                "metric_type": 'IP',
                "offset": 0,
                "ignore_growing": False,
                "params": {"nprobe": 32}
            }

            expr = f"document_id in {file_uuid} && state == 1"

            result = self.milvus_client.search(
                collection_name=collection_name,
                data=query_vectors,
                limit=top_k,
                anns_field="embedding",
                search_params=search_params,
                filter=expr,
                output_fields=["content", "document_id"]
            )
            logger.info(f"查询的结果为：{result}")
            out_result = list()
            for i in range(len(result[0])):
                if result[0][i]["distance"] >= threshold:
                    out_result.append(
                        {
                            "distance": result[0][i]["distance"],
                            "document_id": result[0][i]["entity"]["document_id"],
                            "content": result[0][i]["entity"]["content"],
                        }
                    )
            out_result = sorted(out_result, key=lambda x: x["distance"], reverse=True)
            return out_result
        except Exception as e:
            logger.error("search - " + str(e))
            return []

    def delete(self, document_id: str, collection_name: str):
        try:
            result = self.milvus_client.delete(collection_name=collection_name,
                                               filter=f"document_id == '{document_id}'",
                                               # partition_names=user_id,
                                               )
            logger.info(f"删除的结果为：{result}")
            return True
        except Exception as e:
            logger.error("delete - " + str(e))
            return False

    def query(self, file_uuid: List, collection_name: str):
        try:
            out_dict = {}
            for file in file_uuid:
                out_dict[file] = False
                expr = f"document_id == '{file}'"
                result = self.milvus_client.query(
                    collection_name=collection_name,
                    filter=expr,
                    output_fields=["count(*)"],
                )
                if result[0]['count(*)'] != 0:
                    out_dict[file] = True
            logger.info(f"query的结果为: {out_dict}")
            return out_dict
        except Exception as e:
            logger.error("query - " + str(e))

    def query_content(self, document_id: str, collection_name: str, output_fields: List, start_page: int, end_page: int,
                      state: int, query_string: str = None):
        try:
            if query_string:
                if state == 2:
                    expr = f"content like '%{query_string}%' && document_id == '{document_id}'"
                else:
                    expr = f"content like '%{query_string}%' && document_id == '{document_id}' && state == {state}"
            else:
                if state == 2:
                    expr = f"document_id == '{document_id}' && {start_page} <= content_num  <= {end_page}"
                else:
                    expr = f"document_id == '{document_id}' && {start_page} <= content_num  <= {end_page} && state == {state}"
            print(query_string, expr)

            result = self.milvus_client.query(
                collection_name=collection_name,
                filter=expr,
                output_fields=output_fields,
            )

            result = sorted(result, key=lambda x: x['content_num'])
            logger.info(f"query_content的结果为: {result}")
            return result
        except Exception as e:
            logger.error("query_content - " + str(e))
            return []

    def upsert(self, embedding: list, update_str: str, collection_name: str, chunk_id: int):
        try:
            res = self.milvus_client.get(collection_name=collection_name, ids=chunk_id)
            data = res[0]
            data["content"] = update_str
            data["embedding"] = embedding
            data.pop("id")
            self.milvus_client.delete(collection_name=collection_name, filter=f"id == {chunk_id}")
            result = self.milvus_client.insert(data=data, collection_name=collection_name)
            insert_id = list(result["ids"])
            return insert_id
        except Exception as e:
            stack_trace = traceback.format_exc()
            logger.error(f"upsert: {e}\n堆栈:\n{stack_trace}")
            return None

    def update_content_state(self, collection_name: str, chunk_id: int, isEnable: bool):
        try:
            result = self.milvus_client.get(collection_name=collection_name, ids=chunk_id)
            if result:
                data = result[0]
                if isEnable:
                    data["state"] = 1
                else:
                    data["state"] = 0
                data.pop("id")
                self.milvus_client.delete(collection_name=collection_name, filter=f"id == {chunk_id}")
                res = self.milvus_client.insert(data=data, collection_name=collection_name)
                insert_id = res["ids"]
                print(insert_id)
                return insert_id
            return None
        except Exception as e:
            logger.error("upsert - " + str(e))
            return None


mlivus_client = MilvusConn()

if __name__ == '__main__':
    from database.milvus_orm import CollectionNameEnum, KnowledgeMilvusModelWithLarge, KnowledgeMilvusModelWithSmall

    mlivus_client = MilvusConn()
    mlivus_client.create_collection(CollectionNameEnum.KNOWLEDGE_BASE_LARGE.value, KnowledgeMilvusModelWithLarge)
    mlivus_client.create_collection(CollectionNameEnum.KNOWLEDGE_BASE_SMALL.value, KnowledgeMilvusModelWithSmall)
