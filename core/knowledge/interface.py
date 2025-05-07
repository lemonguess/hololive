# coding: utf-8
from typing import List, Dict

from rag. import default_embedding
from database import mlivus_client
from knowledgeBase.models import *
# from knowledgeBase.util.enum import EMBEDDING_MAP, EmbeddingType
from knowledgeBase.util.file_parse import embed_insert_data
from knowledgeBase.util.enum import *


def search_interface(query_string: str, document_id: List, top_k: int = 5, threshold: float = 0.5):
    try:
        query_emd = default_embedding.encode(model_name=EmbeddingType.BgeLarge.value, texts=[query_string])
        res = mlivus_client.search(query_emd, document_id, EMBEDDING_MAP[EmbeddingType.BgeLarge.value],
                                   top_k, threshold)
        return res
    except Exception as e:
        print(e)
        return []


def parse_and_search(params: Dict, query_string: str, knowledge_ids: List):
    join_type = params["join_type"]
    top_k = params["top_k"]
    threshold = params["threshold"]
    max_tokens = params["max_tokens"]
    if join_type == JoinType.power.value:
        top_k = 3
    document_ids = list()
    document_result = KnowledgeInfo.select(KnowledgeInfo.document_id).where(
        KnowledgeInfo.knowledge_id.in_(knowledge_ids)).execute()
    for res in document_result:
        document_ids.append(res.document_id)
    res = search_interface(query_string, document_ids, top_k, threshold)
    out_list = list()
    out_str = ""
    for i in range(len(res)):
        if len(out_str) > max_tokens:
            break
        out_str += res[i]["content"].replace('<qaspliter>', '\n')
        out_list.append(
            {
                "content": res[i]["content"],
                "file_name": res[i]["document_id"].split("_")[-1],
            }
        )
    return out_list


def get_file_content(document_id: str, start_page: int, end_page: int, state: int = 2, query_string: str = None):
    try:

        result = mlivus_client.query_content(document_id=document_id, collection_name=EMBEDDING_MAP[EmbeddingType.BgeLarge.value],
                                             output_fields=["content_num", "content", "state"], state=state,
                                             start_page=start_page, end_page=end_page, query_string=query_string)
        return result
    except Exception as e:
        return []


def update_content_state(chunk_id: int, isEnable: bool):
    try:
        res = mlivus_client.update_content_state(collection_name=EMBEDDING_MAP[EmbeddingType.BgeLarge.value],
                                                 chunk_id=chunk_id, isEnable=isEnable)
        if res:
            return res
        return False
    except Exception as e:
        return False


def update_content(chunk_id: int, update_str: str):
    chunk_list = [update_str]
    embedding = default_embedding.encode(model_name=EmbeddingType.BgeLarge.value, texts=chunk_list,
                                         batch_size=len(chunk_list))
    res = mlivus_client.upsert(embedding=embedding[0], chunk_id=chunk_id, update_str=update_str,
                               collection_name=EMBEDDING_MAP[EmbeddingType.BgeLarge.value])
    return res


def add_content(add_str: str, document_id: str, knowledge_id: str, content_num: int):
    chunk_list = [add_str]
    embedding = default_embedding.encode(model_name=EmbeddingType.BgeLarge.value, texts=chunk_list,
                                         batch_size=len(chunk_list))
    res = embed_insert_data(chunk_list=chunk_list, embedding=embedding, document_id=document_id,
                            knowledge_id=knowledge_id, collection_name=EMBEDDING_MAP[EmbeddingType.BgeLarge.value],
                            content_len=0, i=content_num+1, is_add=True)
    return res


def get_document_state(document_id: str, state: int):
    res = mlivus_client.get_state(document_id=document_id, state=state,
                                  output_fields=["content_num", "content", "state"],
                                  collection_name=EMBEDDING_MAP[EmbeddingType.BgeLarge.value])
    return res


def delete_file_content(knowledge_id: str, document_id: str):
    try:
        result = KnowledgeInfo.select().where(KnowledgeInfo.document_id == document_id).execute()
        content_num = 0
        file_size = 0
        file_total_size = 0
        for res in result:
            content_num = res.content_num
            file_size = res.file_size
            file_total_size = res.file_total_size
        result = mlivus_client.delete(document_id=document_id,
                                      collection_name=EMBEDDING_MAP[EmbeddingType.BgeLarge.value])
        Knowledge.update(
            file_num=Knowledge.file_num - 1, file_total_size=Knowledge.file_total_size - file_total_size,
            file_split_num=Knowledge.file_split_num - content_num, file_size=Knowledge.file_size - file_size).where(
            Knowledge.knowledge_id == knowledge_id).execute()
        return result
    except Exception as e:
        return False


if __name__ == '__main__':
    ...

