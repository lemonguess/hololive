# coding: utf-8
import datetime

from peewee import AutoField, CharField, DateTimeField, IntegerField, TextField

from database.postgres_pool_service import BaseModel


class KnowledgeInfo(BaseModel):
    id = AutoField(primary_key=True)
    knowledge_id = CharField(max_length=64, help_text="知识库唯一id")
    file_name = CharField(max_length=2000, help_text="文件名称")
    file_url = CharField(max_length=2000, help_text="文件url地址")
    spliter_id = CharField(max_length=64, help_text="分割器唯一id")
    document_id = CharField(index=True, max_length=2000, help_text="文件id")
    chunk_size = IntegerField(help_text="分割字符数")
    max_overlap = IntegerField(help_text="最大重叠字符数", default=0)
    state = IntegerField(help_text="文件解析状态，1为上传，0为失败，2为解析成功，3为正在解析")
    content_num = IntegerField(help_text="文件分段数", default=0)
    file_size = IntegerField(help_text="文件总大小, 单位为MB", default=0)
    file_total_size = IntegerField(help_text="文件总字符数", default=0)
    split_label = CharField(max_length=1000, help_text="分割标识符", null=True)
    code_classify = CharField(max_length=64, help_text="代码分割语言", null=True)
    split_type = IntegerField(help_text="文件分割格式0正常 1qa对", default=0)
    create_time = DateTimeField(default=datetime.datetime.now)
    update_time = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'knowledge_info'


class EmbeddingModel(BaseModel):
    id = AutoField(primary_key=True)
    embedding_name = CharField(index=True, max_length=256, help_text="embedding模型名称")
    dim = IntegerField(help_text="模型维度")
    collection_name = CharField(max_length=256, help_text="对应向量数据库名称")
    create_time = DateTimeField(default=datetime.datetime.now)
    update_time = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'embedding_info'


class Knowledge(BaseModel):
    id = AutoField(primary_key=True)
    knowledge_id = CharField(max_length=64, index=True, help_text="知识库唯一id")
    knowledge_name = CharField(max_length=1000, help_text="知识库名称")
    knowledge_desc = TextField(help_text="知识库描述", null=True)
    file_num = IntegerField(help_text="文件总数", default=0)
    file_size = IntegerField(help_text="文件总大小, 单位为MB", default=0)
    file_total_size = IntegerField(help_text="文件总字符数", default=0)
    file_split_num = IntegerField(help_text="分段总数", default=0)
    # embedding_name = CharField(max_length=256, help_text="embedding模型名称")
    # collection_name = CharField(max_length=256, help_text="对应向量数据库名称")
    # embedding_name = ForeignKeyField(EmbeddingModel, backref='knowledge', to_field='embedding_name',)
    # top_n = IntegerField(help_text="所选top几")
    # threshold = FloatField(help_text="查询阈值")
    create_time = DateTimeField(default=datetime.datetime.now)
    update_time = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'knowledge'


class SpliterModel(BaseModel):
    id = AutoField(primary_key=True)
    spliter_id = CharField(max_length=64, help_text="分割器唯一id")
    spliter = CharField(max_length=128, help_text="分割器")
    create_time = DateTimeField(default=datetime.datetime.now)
    update_time = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'spliter'


tables = [EmbeddingModel, KnowledgeInfo, Knowledge, SpliterModel]
