from typing import (
    Optional,
    List, Dict, Any
)
from typing import Literal
from pydantic import BaseModel

class AddBaseModelAPIParameters(BaseModel):
    user_provider_uuid: Optional[str]
    imodel_type: Optional[str]
    description: Optional[str] = None
    name: Optional[str]
    config: Optional[Dict[str, Any]] = None


class UpdateBaseProviderAPIParameters(BaseModel):
    provider_uuid: Optional[str]
    icon: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None

class DeleteBaseProviderAPIParameters(BaseModel):
    provider_uuid: Optional[str]

class AddUserProviderAPIParameters(BaseModel):
    user_uuid: Optional[str]
    provider_uuid: Optional[str]
    api_key: Optional[str]
    base_url: Optional[str]

class UpdateUserProviderAPIParameters(BaseModel):
    user_provider_uuid: Optional[str]
    api_key: Optional[str] = None
    base_url: Optional[str] = None

class DeleteUserProviderAPIParameters(BaseModel):
    user_provider_uuid: Optional[str]

class SearchBaseProviderAPIParameters(BaseModel):
    uuid_list: List[str]

class SearchUserProviderAPIParameters(BaseModel):
    uuid_list: List[str]