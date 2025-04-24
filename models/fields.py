from pydantic import BaseModel
from typing import Optional
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

class EmbeddingConf(BaseModel):
    model_name: str
    text: str