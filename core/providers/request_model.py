from typing import (
    Optional,
    List, Dict, Any
)
from typing import Literal
from pydantic import BaseModel

class AddBaseProviderAPIParameters(BaseModel):
    icon: Optional[str]
    name: Optional[str]
    description: Optional[str]

class UpdateBaseProviderAPIParameters(BaseModel):
    icon: Optional[str]
    name: Optional[str]
    description: Optional[str]
    provider_uuid: Optional[str]

class DeleteBaseProviderAPIParameters(BaseModel):
    provider_uuid: Optional[str]

class AddUserProviderAPIParameters(BaseModel):
    user_uuid: Optional[str]
    provider_uuid: Optional[str]
    api_key: Optional[str]

class UpdateUserProviderAPIParameters(BaseModel):
    user_provider_uuid: Optional[str]
    api_key: Optional[str]

class SearchBaseProviderAPIParameters(BaseModel):
    uuid_list: List[str]

class SearchUserProviderAPIParameters(BaseModel):
    uuid_list: List[str]





