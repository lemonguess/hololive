from typing import Optional
from pydantic import BaseModel

class UserRegisterAPIParameters(BaseModel):
    username: Optional[str]
    password: Optional[str]

class AlterRoleAPIParameters(BaseModel):
    user_id: Optional[str]
    role: Optional[int]

