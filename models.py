from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from datetime import datetime
import uuid
from enum import Enum


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
    referral_code: Optional[str] = None  # Used when user is referred by someone

class UserPatch(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    referred_by: Optional[str] = None  # UUID of user who referred this user
    referral_code: str  # Unique code for referring others

    class Config:
        from_attributes = True

class PaginatedUsers(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[User]

class Friendship(BaseModel):
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user1_uuid: str
    user2_uuid: str
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True

class FriendshipResponse(BaseModel):
    friendship: Friendship
    friend: User  # The other user in the friendship

class UserWithFriends(User):
    friends: List[User] = []
    pending_requests: List[FriendshipResponse] = []
    sent_requests: List[FriendshipResponse] = []

class ReferralStats(BaseModel):
    total_referrals: int
    successful_referrals: List[User]
