from typing import (
    Optional,
    List, Dict, Any
)
from typing import Literal
from pydantic import BaseModel

class AddBaseModelAPIParameters(BaseModel):
    user_provider_uuid: Optional[str]
    imodel_type: Optional[int]
    description: Optional[str] = None
    name: Optional[str]
    icon: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class UpdateBaseModelAPIParameters(BaseModel):
    imodel_uuid: Optional[str]
    imodel_type: Optional[int] = None
    icon: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class DeleteBaseModelAPIParameters(BaseModel):
    imodel_uuid: Optional[str]