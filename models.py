from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from datetime import datetime
import uuid

# Place holder
class RootResponse(BaseModel):
    message: str
    docs: str
    endpoints: Dict[str, str]

class UserBase(BaseModel):
    email: EmailStr
    name: str
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserPatch(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    created_at: datetime

    class Config:
        from_attributes = True

class PaginatedUsers(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[User]
