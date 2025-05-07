# coding: utf-8
import traceback
import uuid

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from langchain_text_splitters import Language
from starlette import status

from agents.interface import knowledge_get_agent
from config import app_config
from core.knowledge.interface import (search_interface, get_file_content, add_content, get_document_state,
                                     delete_file_content, update_content_state, update_content)
from models.model import KnowledgeInfo, EmbeddingModel, Knowledge, SpliterModel
from core.knowledge.util.api_model import *

from utils.response_util import ResponseUtil
import logging
logger = logging.getLogger(__name__)

knowledge_router = APIRouter(prefix="/knowledgeBase", tags=["knowledgeBase"])


@knowledge_router.post("/file/deal")
async def deal(params: UploadFileModel) -> JSONResponse:
    """
    知识库文件上传处理接口
    Args:
        params: knowledgeId：知识库id
                callback_url：回调url
                file_info：文件信息列表
                     file_no：文件唯一标识
                     file_name：文件名称
                     file_url：文件url链接
                     spliter_id：分割器id
                     chunk_size：分割字符大小
                     max_overlap：最大重叠字数
                     code_classify：当为code分割器时，传入的语言
                     split_label：自定义分割标志符

    Returns: JSONResponse
    """
    try:
        params_dict = params.model_dump()
        out_dict = list()
        for i in range(len(params_dict["file_info"])):
            document_id = params_dict["file_info"][i]["file_no"] + "_" + params_dict["file_info"][i]["file_name"]
            params_dict["file_info"][i]["document_id"] = document_id
            insert_info = {
                "knowledge_id": params_dict["knowledgeId"],
                "file_name": params_dict["file_info"][i]["file_name"],
                "file_url": params_dict["file_info"][i]["file_url"],
                "spliter_id": params_dict["file_info"][i]["spliter_id"] if params_dict["file_info"][i][
                    "spliter_id"] else "",
                "document_id": document_id,
                "chunk_size": params_dict["file_info"][i]["chunk_size"] if params_dict["file_info"][i][
                    "chunk_size"] else 500,
                "max_overlap": params_dict["file_info"][i]["max_overlap"] if params_dict["file_info"][i][
                    "max_overlap"] else 0,
                "state": 1,
                "code_classify": "" if params_dict["file_info"][i]["code_classify"] is None else
                params_dict["file_info"][i]["code_classify"],
                "split_label": "" if params_dict["file_info"][i]["split_label"] is None else
                params_dict["file_info"][i]["split_label"],
                "split_type": params_dict["split_type"],
            }
            KnowledgeInfo.create(**insert_info)
            out_dict.append({
                "file_no": params_dict["file_info"][i]["file_no"],
                "document_id": document_id,
            })
            Knowledge.update(
                file_num=Knowledge.file_num + 1).where(
                Knowledge.knowledge_id == params_dict["knowledgeId"]).execute()
        mq_producer_task(source=app_config.mq_name_config.knowledge_mq_name, params=params_dict, priority=10)
        # file_queue.put(params_dict)
        return ResponseUtil.success(data=out_dict, message="上传成功！")
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error(f"新增文件异常: {e}\n堆栈:\n{stack_trace}")
        return ResponseUtil.error(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@knowledge_router.put("/file/content/update/state")
async def update_content_state_api(params: FileContentStateModel) -> JSONResponse:
    """
    更改分块内容启用或禁用接口
    Args:
        params: chunk_id：分块标识唯一id
                isEnabled：是否开启，boll类型

    Returns: JSONResponse

    """
    try:
        res = update_content_state(chunk_id=params.chunk_id, isEnable=params.isEnabled)
        if res:
            return ResponseUtil.success(data=list(res)[0], message="修改成功")
        return ResponseUtil.error(message="修改失败")
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error(f"更新异常: {e}\n堆栈:\n{stack_trace}")
        return ResponseUtil.error(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@knowledge_router.put("/file/content/update/text")
async def update_content_text(params: FileContentTextModel) -> JSONResponse:
    """
    更改分块内容接口
    Args:
        params: chunk_id：分块标识唯一id
                update_str：需要更新的内容

    Returns: JSONResponse

    """
    try:
        res = update_content(chunk_id=params.chunk_id, update_str=params.update_str)
        if res:
            return ResponseUtil.success(data=res[0], message="修改成功")
        return ResponseUtil.error(message="修改失败")
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error(f"更新异常: {e}\n堆栈:\n{stack_trace}")
        return ResponseUtil.error(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@knowledge_router.post("/file/content/add")
async def add_content_api(params: FileContentAddModel) -> JSONResponse:
    """
    增加分块内容接口
    Args:
        params: knowledgeId：知识库id
                document_id：文件唯一id
                add_str：需要增加的字符内容

    Returns: JSONResponse

    """
    try:
        result = KnowledgeInfo.select().where(KnowledgeInfo.document_id == params.document_id).execute()
        content_num = 0
        for res in result:
            content_num = res.content_num
        res = add_content(knowledge_id=params.knowledgeId, document_id=params.document_id,
                          add_str=params.add_str, content_num=content_num)
        if res:
            return ResponseUtil.success(data="", message="新增成功")
        return ResponseUtil.error(message="新增失败")
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error(f"新增异常: {e}\n堆栈:\n{stack_trace}")
        return ResponseUtil.error(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@knowledge_router.post("/file/search")
async def search(params: SearchFileModel) -> JSONResponse:
    """
    文件检索接口
    Args:
        params: query_string：需要检索的文本内容
                top_n：检索时所的条目，默认为5
                threshold：检索阈值
                document_ids：检索文件唯一id列表

    Returns: JSONResponse

    """
    try:
        search_result = search_interface(query_string=params.query_string, document_id=params.document_ids,
                                         top_k=params.top_n, threshold=params.threshold)
        return ResponseUtil.success(data=search_result, message="查询成功")
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error(f"查询异常: {e}\n堆栈:\n{stack_trace}")
        return ResponseUtil.error(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@knowledge_router.get("/file/state/get/{document_id}/{state}")
async def get_state(document_id: str, state: int) -> JSONResponse:
    """

    Args:
        state:
        document_id:

    Returns:

    """
    try:
        res = get_document_state(document_id=document_id, state=state)
        return ResponseUtil.success(data=res, message="查询成功")
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error(f"查询异常: {e}\n堆栈:\n{stack_trace}")
        return ResponseUtil.error(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@knowledge_router.post("/file/content/get")
async def file_content(params: ContentFileModel) -> JSONResponse:
    """
    获取分块内容接口
    Args:
        params: knowledgeId：知识库唯一id
                document_id：文件唯一id
                start_num：起始页
                end_num：结束页
                query_string：模糊查询文本

    Returns: JSONResponse

    """
    try:
        result = KnowledgeInfo.select().where(KnowledgeInfo.document_id == params.document_id).execute()
        content_num = 0
        for item in result:
            content_num = item.content_num
        res = get_file_content(
            document_id=params.document_id,
            start_page=params.start_num,
            end_page=params.end_num,
            state=params.state,
            query_string=params.query_string
        )
        # content_num = len(res)
        out_data = {
            "content_all_num": content_num,
            "res": res,
        }
        return ResponseUtil.success(data=out_data, message="查询成功")
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error(f"查询异常: {e}\n堆栈:\n{stack_trace}")
        return ResponseUtil.error(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@knowledge_router.delete("/file/delete")
async def file_delete(params: DeleteFileModel) -> JSONResponse:
    """
    文件删除接口
    Args:
        params: knowledgeId：知识库id
                document_id：文件id

    Returns: JSONResponse

    """
    try:
        KnowledgeInfo.update(state=0).where(KnowledgeInfo.document_id == params.document_id).execute()
        res = delete_file_content(knowledge_id=params.knowledgeId, document_id=params.document_id)
        if res:
            KnowledgeInfo.delete().where(KnowledgeInfo.document_id == params.document_id).execute()
            return ResponseUtil.success(data="", message="删除成功")
        return ResponseUtil.error(message="删除失败，异常错误！")
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error(f"删除异常: {e}\n堆栈:\n{stack_trace}")
        return ResponseUtil.error(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@knowledge_router.post("/file/deal/refresh")
async def file_re_deal(params: RefreshFileModel) -> JSONResponse:
    try:
        res = delete_file_content(knowledge_id=params.knowledgeId, document_id=params.document_id)
        if res:
            KnowledgeInfo.delete().where(KnowledgeInfo.document_id == params.document_id).execute()
            # return ResponseUtil.success(data="", message="删除成功")
            params_dict = params.model_dump()
            out_dict = list()
            for i in range(len(params_dict["file_info"])):
                document_id = params_dict["file_info"][i]["file_no"] + "_" + params_dict["file_info"][i]["file_name"]
                params_dict["file_info"][i]["document_id"] = document_id
                insert_info = {
                    "knowledge_id": params_dict["knowledgeId"],
                    "file_name": params_dict["file_info"][i]["file_name"],
                    "file_url": params_dict["file_info"][i]["file_url"],
                    "spliter_id": params_dict["file_info"][i]["spliter_id"] if params_dict["file_info"][i][
                        "spliter_id"] else "",
                    "document_id": document_id,
                    "chunk_size": params_dict["file_info"][i]["chunk_size"],
                    "max_overlap": params_dict["file_info"][i]["max_overlap"] if params_dict["file_info"][i][
                        "max_overlap"] else 0,
                    "state": 1,
                    "code_classify": "" if params_dict["file_info"][i]["code_classify"] is None else
                    params_dict["file_info"][i]["code_classify"],
                    "split_label": "" if params_dict["file_info"][i]["split_label"] is None else
                    params_dict["file_info"][i]["split_label"],
                    "split_type": params_dict["split_type"],
                }
                KnowledgeInfo.create(**insert_info)
                out_dict.append({
                    "file_no": params_dict["file_info"][i]["file_no"],
                    "document_id": document_id,
                })
                Knowledge.update(
                    file_num=Knowledge.file_num + 1).where(
                    Knowledge.knowledge_id == params_dict["knowledgeId"]).execute()
            mq_producer_task(source=app_config.mq_name_config.knowledge_mq_name, params=params_dict, priority=10)
            # file_queue.put(params_dict)
            return ResponseUtil.success(data=out_dict, message="正在重新处理中！")
        return ResponseUtil.error(message="异常错误")
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error(f"重新处理异常: {e}\n堆栈:\n{stack_trace}")
        return ResponseUtil.error(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@knowledge_router.post("/list")
async def file_content(params: KnowledgeListModel) -> JSONResponse:
    """
    获取知识库列表
    Args:
        params: knowledgeIds：知识库id列表

    Returns: JSONResponse

    """
    try:
        result = Knowledge.select().where(Knowledge.knowledge_id.in_(params.knowledgeIds)).execute()
        out_list = [
            {
                "id": res.id,
                "knowledge_id": res.knowledge_id,
                "knowledge_name": res.knowledge_name,
                "file_num": res.file_num,
                "file_size": res.file_size,
                "file_total_size": res.file_total_size,
                "file_split_num": res.file_split_num,
                "create_time": res.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for res in result
        ]
        return ResponseUtil.success(data=out_list, message="查询成功")
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error(f"查询异常: {e}\n堆栈:\n{stack_trace}")
        return ResponseUtil.error(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@knowledge_router.get("/detail/{knowledgeId}")
async def search(knowledgeId: str) -> JSONResponse:
    """
    获取某个知识库底下的文件信息
    Args:
        knowledgeId: knowledgeId：知识库id

    Returns: JSONResponse

    """
    try:
        res = KnowledgeInfo.select().where(KnowledgeInfo.knowledge_id == knowledgeId).execute()
        out_info = []
        for i in range(len(res)):
            info = {
                "document_id": res[i].document_id,
                "file_name": res[i].file_name,
                "file_size": res[i].file_size,
                "create_time": res[i].create_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            out_info.append(info)
        return ResponseUtil.success(data=out_info, message="查询成功")
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error(f"查询异常: {e}\n堆栈:\n{stack_trace}")
        return ResponseUtil.error(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@knowledge_router.post("/create")
async def create_knowledge(params: KnowledgeCreateModel) -> JSONResponse:
    """
    创建知识库接口
    Args:
        params: knowledge_name：知识库名称

    Returns: JSONResponse

    """
    try:
        knowledge_id = str(uuid.uuid4())
        if params.knowledge_desc is not None:
            info = {
                "knowledge_id": knowledge_id,
                "knowledge_name": params.knowledge_name,
                "knowledge_desc": params.knowledge_desc,
            }
        else:
            info = {
                "knowledge_id": knowledge_id,
                "knowledge_name": params.knowledge_name,
            }
        Knowledge.create(**info)
        return ResponseUtil.success(data=knowledge_id, message="创建成功")
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error(f"创建异常: {e}\n堆栈:\n{stack_trace}")
        return ResponseUtil.error(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@knowledge_router.delete("/delete/{knowledgeId}")
async def delete_knowledge(knowledgeId: str) -> JSONResponse:
    """
    删除知识库接口，后续更新
    Args:
        params:

    Returns:

    """
    try:
        res = knowledge_get_agent(knowledgeId)
        if res:
            data = {
                "state": 1,
                "message": "删除失败，该知识库关联智能体！"
            }
            return ResponseUtil.success(data=data, message="查询成功")
        KnowledgeInfo.delete().where(KnowledgeInfo.knowledge_id == knowledgeId).execute()
        Knowledge.delete().where(Knowledge.knowledge_id == knowledgeId).execute()
        data = {
            "state": 0,
            "message": "删除成功！"
        }
        return ResponseUtil.success(data=data, message="删除成功！")
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error(f"删除异常: {e}\n堆栈:\n{stack_trace}")
        return ResponseUtil.error(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@knowledge_router.put("/update")
async def update_knowledge(params: KnowledgeUpdateModel) -> JSONResponse:
    """
    更新知识库接口
    Args:
        params: knowledgeId：知识库id
                knowledge_name：知识库名称

    Returns: JSONResponse

    """
    try:
        if params.knowledge_desc is not None:
            update_info = {
                Knowledge.knowledge_name: params.knowledge_name,
                Knowledge.knowledge_desc: params.knowledge_desc,
                Knowledge.update_time: datetime.datetime.now(),
            }
        else:
            update_info = {
                Knowledge.knowledge_name: params.knowledge_name,
                Knowledge.update_time: datetime.datetime.now(),
            }
        res = Knowledge.update(update_info).where(
            Knowledge.knowledge_id == params.knowledgeId).execute()
        return ResponseUtil.success(data="", message="修改成功")
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error(f"修改异常: {e}\n堆栈:\n{stack_trace}")
        return ResponseUtil.error(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@knowledge_router.get("/spliter/get")
async def get_spliter() -> JSONResponse:
    """
    获取分割器接口
    Returns: JSONResponse

    """
    try:
        result = SpliterModel.select().execute()
        out_list = [
            {
                "spliter_id": res.spliter_id,
                "spliter": res.spliter,
                "create_time": res.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for res in result
        ]
        return ResponseUtil.success(data=out_list, message="查询成功！")
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error(f"查询异常: {e}\n堆栈:\n{stack_trace}")
        return ResponseUtil.error(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@knowledge_router.post("/spliter/create")
async def create_spliter(params: SpliterCreateModel) -> JSONResponse:
    """
    创建分割器接口
    Args:
        params: spliter：分割器文本

    Returns:

    """
    try:
        spliter_id = str(uuid.uuid4())
        info = {
            "spliter_id": spliter_id,
            "spliter": params.spliter,
        }
        inst = SpliterModel.create(**info)
        return ResponseUtil.success(data=inst.id, message="新建成功！")
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error(f"新建异常: {e}\n堆栈:\n{stack_trace}")
        return ResponseUtil.error(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@knowledge_router.get("/codeClassify")
async def get_codeClassify() -> JSONResponse:
    """
    获取code分割器时的语言种类接口
    Returns: JSONResponse

    """
    try:
        values = [item.value for item in Language]
        return ResponseUtil.success(data=values, message="查询成功！")
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error(f"查询异常: {e}\n堆栈:\n{stack_trace}")
        return ResponseUtil.error(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
