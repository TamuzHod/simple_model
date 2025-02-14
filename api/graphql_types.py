from typing import List, Optional
import strawberry
from datetime import datetime
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
    total_count: int = 0  # Set default value to 0

@strawberry.type
class User:
    """Represents a user in the system"""
    uuid: str = strawberry.field(description="Unique identifier for the user")
    email: str = strawberry.field(description="User's email address")
    name: str = strawberry.field(description="User's full name")
    is_active: bool = strawberry.field(description="Whether the user is active")
    created_at: datetime = strawberry.field(description="When the user was created")
    updated_at: datetime = strawberry.field(description="When the user was last updated")
    referred_by: Optional[str] = strawberry.field(description="UUID of user who referred this user", default=None)
    referral_code: str = strawberry.field(description="User's unique referral code")

    @classmethod
    def from_db(cls, user_data: dict) -> 'User':
        """Create a User instance from database data"""
        # Remove MongoDB's _id field if present
        user_dict = user_data.copy()
        user_dict.pop('_id', None)
        return cls(**user_dict)

    @strawberry.field
    async def friends(
        self,
        first: Optional[int] = 10,
        after: Optional[str] = None
    ) -> UserConnection:
        """Get user's friends with pagination"""
        friends, has_next_page = await UserService.get_friends(
            user_uuid=self.uuid,
            limit=first,
            cursor=after
        )

        edges = []
        for friend in friends:
            edges.append(
                UserEdge(
                    cursor=str(friend['_id']),
                    node=User.from_db(friend)
                )
            )

        return UserConnection(
            edges=edges,
            page_info=PageInfo(
                has_next_page=has_next_page,
                has_previous_page=bool(after),
                start_cursor=edges[0].cursor if edges else None,
                end_cursor=edges[-1].cursor if edges else None
            ),
            total_count=len(edges)
        )

    @strawberry.field
    async def referred_users(
        self,
        first: Optional[int] = 10,
        after: Optional[str] = None
    ) -> UserConnection:
        """Get users referred by this user"""
        return await resolve_user_connection(
            first=first,
            after=after,
            filter=UserFilter(referred_by=self.uuid)  # Use the proper filter input type
        )

    @strawberry.field
    async def referrer(self) -> Optional['User']:
        """Get the user who referred this user"""
        if not self.referred_by:
            return None
        user_data = await UserService.get_user_by_uuid(self.referred_by)
        if not user_data:
            return None
        return User.from_db(user_data)

    @strawberry.field
    async def friendship_status(self, other_user_uuid: str) -> 'FriendshipStatus':
        return await resolve_friendship_status(self.uuid, other_user_uuid)

    @strawberry.field
    async def mutual_friends(
        self,
        with_user_uuid: str,
        first: Optional[int] = 10,
        after: Optional[str] = None
    ) -> UserConnection:
        """Get mutual friends between this user and another user"""
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
        description="Filter users by name containing this string",
        default=None
    )
    email_contains: Optional[str] = strawberry.field(
        description="Filter users by email containing this string",
        default=None
    )
    is_active: Optional[bool] = strawberry.field(
        description="Filter users by active status",
        default=None
    )
    created_after: Optional[datetime] = strawberry.field(
        description="Filter users created after this datetime",
        default=None
    )
    created_before: Optional[datetime] = strawberry.field(
        description="Filter users created before this datetime",
        default=None
    )
    friend_of: Optional[str] = strawberry.field(
        description="Filter users who are friends with the specified user UUID",
        default=None
    )
    referred_by: Optional[str] = strawberry.field(
        description="Filter users who were referred by the specified user UUID",
        default=None
    )
    
@strawberry.input
class UserOrder:
    field: str
    direction: str

async def resolve_user_connection(
    first: Optional[int] = 10,
    after: Optional[str] = None,
    filter: Optional[UserFilter] = None,
    order_by: Optional[UserOrder] = None
) -> UserConnection:
    filter_params = {}
    if filter:
        # Convert filter to dict and remove None values
        filter_params = {k: v for k, v in filter.__dict__.items() if v is not None}
    
    if order_by:
        order_dict = {"field": order_by.field, "direction": order_by.direction}
    else:
        order_dict = None

    users, has_next_page = await UserService.get_users_with_filters(
        first=first,
        after=after,
        filter_params=filter_params,
        order_by=order_dict
    )

    edges = []
    for user in users:
        edges.append(
            UserEdge(
                cursor=str(user['_id']),
                node=User.from_db(user)
            )
        )

    # Get filtered count instead of total users count
    try:
        total_count = await UserService.get_filtered_users_count(filter_params)
    except Exception:
        total_count = 0  # Fallback to 0 if count query fails

    return UserConnection(
        edges=edges,
        page_info=PageInfo(
            has_next_page=has_next_page,
            has_previous_page=bool(after),
            start_cursor=edges[0].cursor if edges else None,
            end_cursor=edges[-1].cursor if edges else None
        ),
        total_count=total_count
    )

async def resolve_friendship_status(user1_uuid: str, user2_uuid: str) -> FriendshipStatus:
    """
    Resolves the friendship status between two users.
    Returns a FriendshipStatus object containing:
    - are_friends: whether the users are friends
    - friendship_date: when they became friends (if they are friends)
    - friendship_uuid: unique identifier of their friendship (if they are friends)
    """
    status = await UserService.get_friendship_status(user1_uuid, user2_uuid)
    return FriendshipStatus(
        are_friends=status['are_friends'],
        friendship_date=status['friendship_date'],
        friendship_uuid=status['friendship_uuid']
    )

async def resolve_mutual_friends(
    user1_uuid: str,
    user2_uuid: str,
    first: Optional[int] = 10,
    after: Optional[str] = None
) -> UserConnection:
    """Resolve mutual friends between two users"""
    users, has_next_page = await UserService.get_mutual_friends(
        user1_uuid,
        user2_uuid,
        first=first,
        after=after
    )

    edges = [
        UserEdge(
            cursor=str(user['_id']),
            node=User(**user)
        )
        for user in users
    ]

    return UserConnection(
        edges=edges,
        page_info=PageInfo(
            has_next_page=has_next_page,
            has_previous_page=bool(after),
            start_cursor=edges[0].cursor if edges else None,
            end_cursor=edges[-1].cursor if edges else None
        ),
        total_count=len(edges)
    )
