from pydantic import BaseModel
from typing import Optional, List


class OpenaiClientConf(BaseModel):
    api_key: Optional[str] = None
    api_base: Optional[str] = None
class LLMConf(BaseModel):
    api_key: Optional[str]
    base_url: Optional[str] = ""
    model_name: Optional[str]
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0
    # messages: list[dict] = []



class FileListModel(BaseModel):
    file_id_list: List


class FileNameUploadModel(BaseModel):
    file_id: str
    file_name: str

class EmbeddingConf(BaseModel):
    model_name: str
    text: str

class AgentMemory(BaseModel):
    ...

class AgentModel(BaseModel):
    ...

class AgentKnowledge(BaseModel):
    ...

class AgentWebSearch(BaseModel):
    ...

class AgentFileParser(BaseModel):
    ...

class AgentMCP(BaseModel):
    ...

