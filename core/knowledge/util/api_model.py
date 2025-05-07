# coding: utf-8

from typing import List

from pydantic import BaseModel


class FileInfo(BaseModel):
    file_no: str
    file_name: str
    file_url: str
    spliter_id: str | None = None
    chunk_size: int = 128
    max_overlap: int | None = None
    code_classify: str | None = None
    split_label: str | None = None


class UploadFileModel(BaseModel):
    knowledgeId: str
    callback_url: str
    split_type: int = 0
    file_info: List[FileInfo]


class RefreshFileModel(BaseModel):
    knowledgeId: str
    document_id: str
    callback_url: str
    split_type: int = 0
    file_info: List[FileInfo]


class FileContentStateModel(BaseModel):
    chunk_id: int
    isEnabled: bool


class FileContentTextModel(BaseModel):
    chunk_id: int
    update_str: str


class FileContentAddModel(BaseModel):
    knowledgeId: str
    document_id: str
    add_str: str


class SearchFileModel(BaseModel):
    query_string: str
    top_n: int = 5
    threshold: float = 0.5
    document_ids: List


class ContentFileModel(BaseModel):
    knowledgeId: str
    document_id: str
    start_num: int = 1
    end_num: int = 20
    state: int = 2
    query_string: str = None


class DeleteFileModel(BaseModel):
    knowledgeId: str
    document_id: str


class KnowledgeCreateModel(BaseModel):
    knowledge_name: str
    knowledge_desc: str = None


class KnowledgeListModel(BaseModel):
    knowledgeIds: List


class KnowledgeDeleteModel(BaseModel):
    knowledgeId: str


class KnowledgeUpdateModel(BaseModel):
    knowledgeId: str
    knowledge_name: str
    knowledge_desc: str = None


class SpliterCreateModel(BaseModel):
    spliter: str
