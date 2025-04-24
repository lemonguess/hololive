from typing import (
    Optional,
    List
)
from pydantic import BaseModel

class PaginationParameters(BaseModel):
    page: int
    page_size: int


class AddBaseProviderAPIParameters(BaseModel):
    icon: Optional[str]
    name: Optional[str]
    description: Optional[str]

class UpdateBaseProviderAPIParameters(BaseModel):
    provider_id: Optional[str]
    icon: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None

class DeleteBaseProviderAPIParameters(BaseModel):
    provider_id: Optional[str]

class SearchBaseProviderAPIParameters(BaseModel):
    id_list: List[str]







