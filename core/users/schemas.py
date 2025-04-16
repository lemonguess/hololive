from typing import Optional
from pydantic import BaseModel

class UserTokenAPIParameters(BaseModel):
    username: Optional[str]
    password: Optional[str]

class AlterRoleAPIParameters(BaseModel):
    user_id: Optional[str]
    role: Optional[int]

class GetTokenAPIParameters(BaseModel):
    access_token: Optional[str]
    token_type: Optional[str]



