import strawberry
from typing import Optional
from .graphql_types import (
    User, Friendship, ReferralStats, UserConnection,
    UserFilter, UserOrder, resolve_mutual_friends, resolve_user_connection
)
from services.user_service import UserService

@strawberry.type
class Query:
    @strawberry.field
    async def user(self, uuid: str) -> Optional[User]:
        user_data = await UserService.get_user_by_uuid(uuid)
        return User(**user_data) if user_data else None

    @strawberry.field
    async def users(
        self,
        first: Optional[int] = 10,
        after: Optional[str] = None,
        last: Optional[int] = None,
        before: Optional[str] = None,
        filter: Optional[UserFilter] = None,
        order_by: Optional[UserOrder] = None
    ) -> UserConnection:
        return await resolve_user_connection(
            first=first,
            after=after,
            last=last,
            before=before,
            filter=filter,
            order_by=order_by
        )

    @strawberry.field
    async def search_users(
        self,
        query: str,
        first: Optional[int] = 10,
        after: Optional[str] = None
    ) -> UserConnection:
        return await resolve_user_connection(
            first=first,
            after=after,
            search_query=query
        )

    @strawberry.field
    async def friendship(self, uuid: str) -> Optional[Friendship]:
        friendship_data = await UserService.get_friendship(uuid)
        return Friendship(**friendship_data) if friendship_data else None

    @strawberry.field
    async def mutual_friends(
        self,
        user1_uuid: str,
        user2_uuid: str,
        first: Optional[int] = 10,
        after: Optional[str] = None
    ) -> UserConnection:
        return await resolve_mutual_friends(
            user1_uuid,
            user2_uuid,
            first=first,
            after=after
        )

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_user(
        self,
        email: str,
        name: str,
        password: str,
        referral_code: Optional[str] = None
    ) -> User:
        from models import UserCreate
        user_data = await UserService.create_user(
            UserCreate(
                email=email,
                name=name,
                password=password,
                referral_code=referral_code
            )
        )
        return User(**user_data)

    @strawberry.mutation
    async def update_user(
        self,
        uuid: str,
        email: Optional[str] = None,
        name: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Optional[User]:
        from models import UserPatch
        patch_data = {k: v for k, v in {
            'email': email,
            'name': name,
            'is_active': is_active
        }.items() if v is not None}
        
        updated_user = await UserService.patch_user(uuid, UserPatch(**patch_data))
        return User(**updated_user) if updated_user else None

    @strawberry.mutation
    async def delete_user(self, uuid: str) -> bool:
        return await UserService.delete_user(uuid)

    @strawberry.mutation
    async def create_friendship(
        self,
        user1_uuid: str,
        user2_uuid: str
    ) -> Friendship:
        friendship = await UserService.send_friend_request(user1_uuid, user2_uuid)
        return Friendship(**friendship)

    @strawberry.mutation
    async def remove_friendship(
        self,
        user1_uuid: str,
        user2_uuid: str
    ) -> bool:
        return await UserService.remove_friend(user1_uuid, user2_uuid)

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    types=[User, Friendship, ReferralStats, UserConnection]
)
