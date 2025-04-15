from typing import (
    Optional,
    List, Dict, Any
)
from typing import Literal
from pydantic import BaseModel

class CreateAgentAPIParameters(BaseModel):
    name: Optional[str]    # Agent 名称
    description: Optional[str]   # Agent 描述
    avatar_image: Optional[str]   # Agent 头像
    agent_status: Literal[1, 2, 5] = 2  # Agent 状态 {1: 已发布， 2: 草稿， 3: 已下架，5: 违规下架}
    agent_type: Literal[1, 2] = 1  # Agent 类型 {1: 普通智能体， 2: RAG智能体}
    modified: Literal[0, 1] = 1  # Agent 编辑状态 {0: 未修改， 1: 已修改}
    configs: Optional[dict]   # Agent 模型配置
    parameters: Optional[dict]  # Agent 模型参数配置
    proof: Optional[str]   # Agent 模型凭证
    # model_uuid: Optional[str]  # Agent 模型uuid
    temperature: Optional[float] = 0  # 使输出更加随机 默认为 0，如果设置，值域须为 [0, 1]
    max_tokens: Optional[int] = 600  # 聊天完成时生成的最大 token 数。
    system_prompt: Optional[str] = None  # 系统提示词
    opening_statement: Optional[str]  # Agent 开场白
    opening_remarks_issue: Optional[List[str]] = None  # 开场白问题
    is_knowledge: Optional[bool] = False  # 知识库检索增强
    knowledge_config: Optional[Dict] = None  # 知识库检索配置
    entry_parameter: Optional[Dict] = None  # 入参变量
    auto_follow_up: Optional[bool] = False  # 是否自动追问
    websearch_config: Optional[Dict] = None  # 联网搜索配置
    long_term_memory: Optional[bool] = False  # 是否使用长期记忆
    consecutive_memory_num: Optional[int] = 20  # 顺时记忆 轮数 默认 10
    long_term_memory_num: Optional[int] = 20  # 长期记忆 轮数 默认 6
    is_publicity: Optional[bool] = True  # 是否公开
    delisting_cause: Optional[int] = None  # 下架原因
    delisting_info: Optional[str] = None  # 下架详情
    delisting_image: Optional[str] = None  # 下架图片
    knowledge_id_list: Optional[List[int]] = None  # 知识库id列表
    tool_id_list: Optional[List[int]] = None  # 插件id列表
    workflow_id_list: Optional[List[int]] = None  # 工作流id列表
    module_id_list: Optional[List[int]] = None  # 组件 id 列表

class UpdateAgentAPIParameters(BaseModel):
    agent_id: Optional[int] = None  # Agent id
    name: Optional[str] = None  # Agent 名称
    description: Optional[str] = None  # Agent 描述
    avatar_image: Optional[str] = None  # Agent 头像
    agent_status: Optional[Literal[1, 2, 5]] = None  # Agent 状态 {1: 已发布， 2: 草稿， 3: 已下架，5: 违规下架}
    agent_type: Optional[Literal[1, 2]] = None  # Agent 类型 {1: 普通智能体， 2: RAG智能体}
    modified: Optional[Literal[0, 1]] = None  # Agent 编辑状态 {0: 未修改， 1: 已修改}
    configs: Optional[Dict] = None  # Agent 模型配置
    parameters: Optional[Dict] = None  # Agent 模型参数配置
    proof: Optional[str] = None  # Agent 模型凭证
    temperature: Optional[float] = None  # 使输出更加随机，默认为 0，值域须为 [0, 1]
    max_tokens: Optional[int] = None  # 聊天完成时生成的最大 token 数
    system_prompt: Optional[str] = None  # 系统提示词
    opening_statement: Optional[str] = None  # Agent 开场白
    opening_remarks_issue: Optional[List[str]] = None  # 开场白问题
    is_knowledge: Optional[bool] = None  # 知识库检索增强
    knowledge_config: Optional[Dict] = None  # 知识库检索配置
    entry_parameter: Optional[Dict] = None  # 入参变量
    auto_follow_up: Optional[bool] = None  # 是否自动追问
    websearch_config: Optional[Dict] = None  # 联网搜索配置
    long_term_memory: Optional[bool] = None  # 是否使用长期记忆
    consecutive_memory_num: Optional[int] = None  # 顺时记忆轮数，默认 10
    long_term_memory_num: Optional[int] = None  # 长期记忆轮数，默认 6
    is_publicity: Optional[bool] = None  # 是否公开
    is_delete: Optional[bool] = None  # 是否删除
    delisting_cause: Optional[int] = None  # 下架原因
    delisting_info: Optional[str] = None  # 下架详情
    delisting_image: Optional[str] = None  # 下架图片
    knowledge_id_list: Optional[List[int]] = None  # 知识库id列表
    tool_id_list: Optional[List[int]] = None  # 插件id列表
    workflow_id_list: Optional[List[int]] = None  # 工作流id列表
    module_id_list: Optional[List[int]] = None  # 组件 id 列表

class GetAllAgentAPIParameters(BaseModel):
    current: Optional[int] = 1
    size: Optional[int] = 10
    agent_uuid_list: Optional[List[str]] = None
    name: Optional[str] = None  # Agent 名称
    agent_status: Optional[Literal[1, 2, 5]] = None  # Agent 状态 {1: 已发布， 2: 草稿， 3: 已下架，5: 违规下架}
    is_publicity: Optional[bool] = None  # 是否公开
    conditions: Optional[List[Dict]] = None
    release_status: Optional[int] = 0  # 默认查询测试版





class CopyAgentAPIParameters(BaseModel):
    agent_id: Optional[int]


class AgentChatAPIParameters(BaseModel):
    agent_id: Optional[int] = 0
    user_id: Optional[str]
    conversation_id: Optional[str]
    messages: List[Dict[str, Any]]
    agent_uuid: Optional[str] = ""
    # temperature: Optional[float] = None
    # max_tokens: Optional[int] = None
    # model_configs: Optional[Dict[str, Any]] = None
    # model_proof: Optional[str] = None
    # is_knowledge: Optional[bool] = None  # 知识库检索增强
    # knowledge_config: Optional[dict] = None  # 知识库检索配置
    entry_parameter: Optional[dict] = None  # 入参变量
    # system_prompt: Optional[str] = None  # 系统提示词
    stream: Optional[bool] = True
    release_status: Optional[int] = 0
    distance: Optional[float] = 0.5
    async_event: Optional[bool] = None
    websearch_config: Optional[Dict] = None
    file_list: Optional[List[Dict[str, Any]]] = None  # 文件列表
    use_api: Optional[bool] = False

class AgentHistoryAPIParameters(BaseModel):
    agent_id: Optional[int] = None
    user_id: Optional[str]  = None
    conversation_id: Optional[str]  = None
    current: Optional[int] = 1
    size: Optional[int] = 10
    agent_uuid: Optional[str] = None



