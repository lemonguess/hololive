from typing import (
    Optional,
    List, Dict, Any
)
from typing import Literal
from pydantic import BaseModel

class AddBaseModelAPIParameters(BaseModel):
    provider_id: Optional[str]
    type: Optional[str]
    description: Optional[str] = None
    name: Optional[str]
    icon: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class UpdateBaseModelAPIParameters(BaseModel):
    model_id: Optional[str]
    type: Optional[str] = None
    icon: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class DeleteBaseModelAPIParameters(BaseModel):
    model_id: Optional[str]