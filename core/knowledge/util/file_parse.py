# coding: utf-8
import subprocess
import traceback

import requests

from database import mlivus_client
from embedding import default_embedding
from knowledgeBase.models.data_model import SpliterModel, KnowledgeInfo, Knowledge
from knowledgeBase.util.enum import EmbeddingType, EMBEDDING_MAP
from utils.logs_service import get_logs
from utils.nlp.chunk import default_split_chunk, custom_split_chunk
from utils.parser import FACTORY, NewCsvParser
from utils.parser.base import parse_xls_to_xlsx
from utils.parser.code_parser import CodeParser
from utils.parser.config import ParserType, SPLITER, filename_type
from utils.parser.tool import get_content

logger = get_logs()


def callback(callback_url: str, document_id: str, state: int, knowledge_id: str, data_len: int = None):
    try:
        body = {
            "document_id": document_id,
            "state": state,
            "data_len": data_len
        }
        if state == 0:
            KnowledgeInfo.update(state=0).where(KnowledgeInfo.document_id == document_id).execute()
            # Knowledge.update(
            #     file_num=Knowledge.file_num + 1).where(
            #     Knowledge.knowledge_id == knowledge_id).execute()
        res = requests.post(callback_url, json=body, timeout=10)
        logger.info(f"知识库回调成功，回调状态码：{res.status_code}，类型：{state}")
    except Exception as e:
        logger.error(f"知识库回调时错误:{str(e)}")
        logger.error(f"知识库回调时错误堆栈:{traceback.format_exc()}")


def embed_insert_data(chunk_list, embedding, document_id, collection_name, knowledge_id, content_len, i=1,
                      callback_url=None, is_add=False):
    insert_data = list()
    i = i
    file_total_size = 0
    for chunk, emd in zip(chunk_list, embedding):
        insert_data.append(
            {
                "document_id": document_id,
                "content_num": i,
                "state": 1,
                "content": chunk,
                "embedding": emd,
            }
        )
        file_total_size += len(chunk)
        i += 1
    res = mlivus_client.insert(data_in=insert_data, collection_name=collection_name, is_add=is_add)
    if res:
        state = 1
        result = KnowledgeInfo.select().where(KnowledgeInfo.document_id == document_id).execute()
        for res_k in result:
            state = res_k.state
        if state == 0:
            return True
        KnowledgeInfo.update(
            content_num=i - 1, file_size=content_len, file_total_size=file_total_size, state=2
        ).where(KnowledgeInfo.document_id == document_id).execute()
        Knowledge.update(
            file_total_size=Knowledge.file_total_size + file_total_size,
            file_split_num=Knowledge.file_split_num + i - 1, file_size=Knowledge.file_size + content_len).where(
            Knowledge.knowledge_id == knowledge_id).execute()
        if callback_url:
            callback(callback_url, document_id, 1, knowledge_id, len(insert_data))
    else:
        if callback_url:
            callback(callback_url, document_id, 0, knowledge_id)
    return res


def parser(file_name: str, content: bytes | str, chunk_size: int, embedding_name: str, collection_name: str,
           document_id: str, knowledge_id: str, callback_url: str, max_overlap: int = None, split_label: str = None):
    try:
        if isinstance(content, str):
            content = get_content(content)
        file_type = filename_type(file_name)
        if file_type == ParserType.XlsParser.value:
            content = parse_xls_to_xlsx(content)
        if file_type == ParserType.OtherParser.value:
            raise Exception("暂不支持的文件类型")
        if file_type == ParserType.DocParser.value:
            logger.info("开启进程解析知识库doc文件")
            process = subprocess.Popen(
                ["catdoc", "-s", "-"],  # "-" 代表从 stdin 读取
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            # 传递二进制数据并获取输出
            output, error = process.communicate(input=content)
            # 检查是否有错误
            if process.returncode != 0:
                raise Exception(f"catdoc 解析失败: {error.decode()}")
            logger.info("doc文件提取成功")
            section: str = output.decode()
            section = section.replace(" ", "").strip()
        else:
            parse_factory = FACTORY[file_type]
            section = parse_factory.parse(content)
        if max_overlap:
            chunk_list = custom_split_chunk(section, chunk_size, max_overlap, split_label)
        else:
            chunk_list = default_split_chunk(section, chunk_size)
        embedding = default_embedding.encode(model_name=embedding_name, texts=chunk_list,
                                             batch_size=len(chunk_list))
        # 保存数据库
        embed_insert_data(chunk_list, embedding, document_id, collection_name, knowledge_id, len(content),
                          callback_url=callback_url)
    except Exception as e:
        logger.error(f"知识库解析错误:{str(e)}")
        logger.error(f"解析异常堆栈:{traceback.format_exc()}")
        callback(callback_url, document_id, 0, knowledge_id)


def parse_code(content: bytes | str, chunk_size: int, max_overlap: int, code_classify: str, embedding_name: str,
               collection_name: str, document_id: str, knowledge_id: str, callback_url: str, split_label: str):
    try:
        parse_factory = FACTORY[ParserType.CodeParser.value]
        section = parse_factory.parse(content)
        section = CodeParser.split_chunk(section, code_classify, chunk_size, max_overlap)
        if max_overlap:
            chunk_list = custom_split_chunk(section, chunk_size, max_overlap, split_label)
        else:
            chunk_list = default_split_chunk(section, chunk_size)
        embedding = default_embedding.encode(model_name=embedding_name, texts=chunk_list,
                                             batch_size=len(chunk_list))
        # 保存数据库
        embed_insert_data(chunk_list, embedding, document_id, collection_name, knowledge_id, len(content),
                          callback_url=callback_url)
    except Exception as e:
        callback(callback_url, document_id, 0, knowledge_id)
        logger.error(f"知识库解析错误:{str(e)}")
        logger.error(f"解析异常堆栈:{traceback.format_exc()}")


def _format_qa_result(result):
    # 将解析结果按问答对分割
    #问题：问题1; 答案：答案1	问题：问题2; 答案：答案2	问题：问题3; 答案：答案3 转成['问题1<qaspliter>答案1', '问题<qaspliter>答案2', '问题3<qaspliter>答案3']
    entries = result.split('\t')
    formatted_entries = []
    for entry in entries:
        # 将每个条目按分号分割成键值对
        pairs = entry.split('; ')
        formatted_pairs = []
        key = pairs[0].split('：',1)[1]
        value = pairs[1].split('：',1)[1]
        formatted_pairs.append(f"{key}<qaspliter>{value}")
        formatted_entries.extend(formatted_pairs)
    return formatted_entries


def parse_qa(content: bytes | str, document_id: str,
             knowledge_id: str, callback_url: str) -> bool:
    try:
        csv_parser = NewCsvParser()

        # 解析CSV内容
        result = csv_parser.parse(content)

        chunk_list = _format_qa_result(result)

        embedding = default_embedding.encode(model_name=EmbeddingType.BgeLarge.value, texts=chunk_list,
                                             batch_size=len(chunk_list))
        # 保存数据库
        embed_insert_data(chunk_list, embedding, document_id, EMBEDDING_MAP[EmbeddingType.BgeLarge.value], knowledge_id,
                          len(content),
                          callback_url=callback_url)
        return True
    except Exception as e:
        callback(callback_url, document_id, 0, knowledge_id)
        logger.error(f"知识库解析错误:{str(e)}")
        logger.error(f"解析异常堆栈:{traceback.format_exc()}")
        return False


def parse_by_spliter(spliter_fac_code: int, file_name: str, content: bytes | str, chunk_size: int, document_id: str,
                     knowledge_id: str, callback_url: str, max_overlap: int = None, split_label: str = None,
                     code_classify: str = None) -> bool:
    try:
        if spliter_fac_code == 1 or spliter_fac_code == 3:
            parser(file_name=file_name, content=content, chunk_size=chunk_size, max_overlap=max_overlap,
                   split_label=split_label, embedding_name=EmbeddingType.BgeLarge.value, knowledge_id=knowledge_id,
                   collection_name=EMBEDDING_MAP[EmbeddingType.BgeLarge.value], document_id=document_id,
                   callback_url=callback_url)
        if spliter_fac_code == 2:
            if code_classify is None:
                return False
            parse_code(content=content, chunk_size=chunk_size, max_overlap=max_overlap, code_classify=code_classify,
                       embedding_name=EmbeddingType.BgeLarge.value, knowledge_id=knowledge_id,
                       callback_url=callback_url,
                       collection_name=EMBEDDING_MAP[EmbeddingType.BgeLarge.value], document_id=document_id,
                       split_label=split_label, )
        return True
    except Exception as e:
        callback(callback_url, document_id, 0, knowledge_id)
        logger.error(f"知识库解析错误:{str(e)}")
        logger.error(f"解析异常堆栈:{traceback.format_exc()}")
        return False


def submit(file_name: str, file_url: bytes | str, chunk_size: int, document_id: str, knowledge_id: str,
           callback_url: str, max_overlap: int = None, split_label: str = None, spliter_id: str = None,
           code_classify: str = None):
    try:
        callback(callback_url, document_id, 2, knowledge_id)
        KnowledgeInfo.update(state=3).where(KnowledgeInfo.document_id == document_id).execute()
        if spliter_id:
            result = SpliterModel.select().where(SpliterModel.spliter_id == spliter_id).execute()
            spliter = ""
            for res in result:
                spliter = res.spliter
        else:
            spliter = "Character TextSplitter (字符分割器)"
        spliter_fac_code = SPLITER[spliter]
        content = get_content(file_url)
        # 解析
        result = parse_by_spliter(spliter_fac_code, file_name, content, chunk_size, document_id, knowledge_id,
                                  callback_url,
                                  max_overlap, split_label, code_classify)
        if not result:
            callback(callback_url, document_id, 0, knowledge_id)
    except Exception as e:
        callback(callback_url, document_id, 0, knowledge_id)
        logger.error(f"知识库解析错误:{str(e)}")
        logger.error(f"解析异常堆栈:{traceback.format_exc()}")


def submit_qa(file_url: bytes | str, document_id: str, knowledge_id: str,
              callback_url: str):
    try:
        callback(callback_url, document_id, 2, knowledge_id)
        KnowledgeInfo.update(state=3).where(KnowledgeInfo.document_id == document_id).execute()
        content = get_content(file_url)
        # 解析
        result = parse_qa(content, document_id, knowledge_id,
                          callback_url)
        if not result:
            callback(callback_url, document_id, 0, knowledge_id)
    except Exception as e:
        callback(callback_url, document_id, 0, knowledge_id)
        logger.error(f"知识库解析错误:{str(e)}")
        logger.error(f"解析异常堆栈:{traceback.format_exc()}")
