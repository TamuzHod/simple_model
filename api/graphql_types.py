from typing import List, Optional
import strawberry
from datetime import datetime
from dataclasses import dataclass
from services.user_service import UserService

@strawberry.type
class UserEdge:
    cursor: str
    node: 'User'

@strawberry.type
class PageInfo:
    has_next_page: bool
    has_previous_page: bool
    start_cursor: Optional[str]
    end_cursor: Optional[str]

@strawberry.type
class UserConnection:
    edges: List[UserEdge]
    page_info: PageInfo
    total_count: int

@strawberry.type
class User:
    """Represents a user in the system"""
    uuid: str = strawberry.field(description="Unique identifier for the user")
    email: str = strawberry.field(description="User's email address")
    name: str = strawberry.field(description="User's full name")
    is_active: bool = strawberry.field(description="Whether the user is active")
    created_at: datetime = strawberry.field(description="When the user was created")
    updated_at: datetime = strawberry.field(description="When the user was last updated")
    referred_by: Optional[str] = strawberry.field(description="UUID of user who referred this user")
    referral_code: str = strawberry.field(description="User's unique referral code")

    @strawberry.field
    async def friends(
        self,
        first: Optional[int] = None,
        after: Optional[str] = None,
        last: Optional[int] = None,
        before: Optional[str] = None
    ) -> UserConnection:
        return await resolve_user_connection(
            self.uuid,
            first=first,
            after=after,
            last=last,
            before=before,
            friend_filter=True
        )

    @strawberry.field
    async def referred_users(
        self,
        first: Optional[int] = None,
        after: Optional[str] = None,
        last: Optional[int] = None,
        before: Optional[str] = None
    ) -> UserConnection:
        return await resolve_user_connection(
            self.uuid,
            first=first,
            after=after,
            last=last,
            before=before,
            referral_filter=True
        )

    @strawberry.field
    async def referrer(self) -> Optional['User']:
        if not self.referred_by:
            return None
        user_data = await UserService.get_user_by_uuid(self.referred_by)
        return User(**user_data) if user_data else None

    @strawberry.field
    async def friendship_status(self, other_user_uuid: str) -> 'FriendshipStatus':
        return await resolve_friendship_status(self.uuid, other_user_uuid)

    @strawberry.field
    async def mutual_friends(
        self,
        with_user_uuid: str,
        first: Optional[int] = None,
        after: Optional[str] = None
    ) -> UserConnection:
        return await resolve_mutual_friends(
            self.uuid,
            with_user_uuid,
            first=first,
            after=after
        )

@strawberry.type
class FriendshipStatus:
    are_friends: bool
    friendship_date: Optional[datetime]
    friendship_uuid: Optional[str]

@strawberry.type
class Friendship:
    uuid: str
    user1_uuid: str
    user2_uuid: str
    created_at: datetime

    @strawberry.field
    async def user1(self) -> User:
        user_data = await UserService.get_user_by_uuid(self.user1_uuid)
        return User(**user_data)

    @strawberry.field
    async def user2(self) -> User:
        user_data = await UserService.get_user_by_uuid(self.user2_uuid)
        return User(**user_data)

@strawberry.type
class ReferralStats:
    total_referrals: int
    successful_referrals: List[User]
    referral_code: str

@strawberry.input
class UserFilter:
    """Filter options for users query"""
    name_contains: Optional[str] = strawberry.field(
        description="Filter users by name containing this string"
    )
    email_contains: Optional[str] = strawberry.field(
        description="Filter users by email containing this string"
    )
    is_active: Optional[bool] = strawberry.field(
        description="Filter users by active status"
    )
    created_after: Optional[datetime] = strawberry.field(
        description="Filter users created after this datetime"
    )
    created_before: Optional[datetime] = strawberry.field(
        description="Filter users created before this datetime"
    )

@strawberry.input
class UserOrder:
    field: str
    direction: str

async def resolve_user_connection(
    user_uuid: Optional[str] = None,
    first: Optional[int] = None,
    after: Optional[str] = None,
    last: Optional[int] = None,
    before: Optional[str] = None,
    friend_filter: bool = False,
    referral_filter: bool = False,
    filter: Optional[UserFilter] = None,
    order_by: Optional[UserOrder] = None
) -> UserConnection:
    # Convert filter to dict for UserService
    filter_params = None
    if filter:
        filter_params = {
            'name_contains': filter.name_contains,
            'email_contains': filter.email_contains,
            'is_active': filter.is_active,
            'created_after': filter.created_after,
            'created_before': filter.created_before
        }
        # Remove None values
        filter_params = {k: v for k, v in filter_params.items() if v is not None}

    # Convert order_by to dict for UserService
    order_params = None
    if order_by:
        order_params = {
            'field': order_by.field,
            'direction': order_by.direction
        }

    # Get users with cursor-based pagination
    users, has_next_page = await UserService.get_users_with_cursor(
        limit=first or 10,
        cursor=after,
        filter_params=filter_params,
        order_by=order_params
    )

    # Create edges
    edges = [
        UserEdge(
            cursor=str(user['_id']),
            node=User(**user)
        ) for user in users
    ]

    # Create page info
    page_info = PageInfo(
        has_next_page=has_next_page,
        has_previous_page=False if not before else True,
        start_cursor=edges[0].cursor if edges else None,
        end_cursor=edges[-1].cursor if edges else None
    )

    # Get total count (this might need optimization for large datasets)
    total_count = await UserService.get_users_count()

    return UserConnection(
        edges=edges,
        page_info=page_info,
        total_count=total_count
    )

async def resolve_friendship_status(user1_uuid: str, user2_uuid: str) -> FriendshipStatus:
    # Implementation to check friendship status
    # This would be implemented in UserService
    pass

async def resolve_mutual_friends(
    user1_uuid: str,
    user2_uuid: str,
    first: Optional[int] = None,
    after: Optional[str] = None
) -> UserConnection:
    # Implementation to find mutual friends
    # This would be implemented in UserService
    pass
