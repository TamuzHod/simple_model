from datetime import datetime
import secrets
from typing import Optional, Dict, Any, Tuple, List
import uuid
from models import UserBase, UserCreate, UserPatch
from database import Database
from utils.pagination import CursorPagination
from bson import ObjectId

class UserService:
    @staticmethod
    def _generate_referral_code() -> str:
        return secrets.token_urlsafe(8)

    @staticmethod
    async def _ensure_unique_referral_code() -> str:
        db = Database.get_db()
        while True:
            code = UserService._generate_referral_code()
            existing = await db.users.find_one({"referral_code": code})
            if not existing:
                return code

    @staticmethod
    async def create_user(user: UserCreate) -> dict:
        db = Database.get_db()
        user_dict = user.model_dump()
        
        # Handle password (in real app, would hash it)
        del user_dict["password"]
        
        # Generate unique referral code
        user_dict["referral_code"] = await UserService._ensure_unique_referral_code()
        
        # Handle referral
        if user.referral_code:
            referrer = await db.users.find_one({"referral_code": user.referral_code})
            if referrer:
                user_dict["referred_by"] = referrer["uuid"]
        
        # Add timestamps
        now = datetime.now()
        user_dict.update({
            "uuid": str(ObjectId()),
            "created_at": now,
            "updated_at": now
        })
        
        await db.users.insert_one(user_dict)
        return user_dict

    @staticmethod
    async def get_referral_stats(user_uuid: str) -> Tuple[int, List[dict]]:
        db = Database.get_db()
        referred_users = await db.users.find(
            {"referred_by": user_uuid}
        ).to_list(length=None)
        return len(referred_users), referred_users

    @staticmethod
    async def send_friend_request(from_uuid: str, to_uuid: str) -> dict:
        db = Database.get_db()
        
        # Check if users exist
        from_user = await db.users.find_one({"uuid": from_uuid})
        to_user = await db.users.find_one({"uuid": to_uuid})
        if not from_user or not to_user:
            raise ValueError("One or both users not found")
        
        # Prevent self-friending
        if from_uuid == to_uuid:
            raise ValueError("Cannot friend yourself")
        
        # Check if friendship already exists
        existing = await db.friendships.find_one({
            "$or": [
                {"user1_uuid": from_uuid, "user2_uuid": to_uuid},
                {"user1_uuid": to_uuid, "user2_uuid": from_uuid}
            ]
        })
        
        if existing:
            raise ValueError("Users are already friends")
        
        # Create new friendship
        friendship = {
            "uuid": str(uuid.uuid4()),
            "user1_uuid": from_uuid,
            "user2_uuid": to_uuid,
            "created_at": datetime.now()
        }
        
        await db.friendships.insert_one(friendship)
        return friendship

    @staticmethod
    async def get_friends(  
        user_uuid: str,
        limit: Optional[int] = 10,
        cursor: Optional[str] = None
    ) -> Tuple[List[dict], bool]:
        """Get friends of a user with pagination"""
        db = Database.get_db()
        
        # Find all friendships where the user is either user1 or user2
        pipeline = [
            {
                "$match": {
                    "$or": [
                        {"user1_uuid": user_uuid},
                        {"user2_uuid": user_uuid}
                    ]
                }
            },
            {
                "$addFields": {
                    "friend_uuid": {
                        "$cond": {
                            "if": {"$eq": ["$user1_uuid", user_uuid]},
                            "then": "$user2_uuid",
                            "else": "$user1_uuid"
                        }
                    }
                }
            },
            {
                "$lookup": {
                    "from": "users",
                    "localField": "friend_uuid",
                    "foreignField": "uuid",
                    "as": "friend"
                }
            },
            {
                "$unwind": "$friend"
            },
            {
                "$replaceRoot": { "newRoot": "$friend" }
            }
        ]

        if cursor:
            pipeline.insert(0, {
                "$match": {
                    "_id": {"$gt": ObjectId(cursor)}
                }
            })

        # Add limit + 1 to check for next page
        pipeline.append({"$limit": limit + 1})
        
        friends = await db.friendships.aggregate(pipeline).to_list(length=None)
        
        has_next_page = len(friends) > limit
        friends = friends[:limit]  # Remove the extra item if it exists
        
        return friends, has_next_page

    @staticmethod
    async def remove_friend(uuid_1: str, uuid_2: str) -> bool:
        db = Database.get_db()
        
        # First check if both users exist
        user = await db.users.find_one({"uuid": uuid_1})
        friend = await db.users.find_one({"uuid": uuid_2})
        if not user or not friend:
            raise ValueError("One or both users not found")
        
        # Then try to find and delete the friendship
        result = await db.friendships.delete_one({
            "$or": [
                {"user1_uuid": uuid_1, "user2_uuid": uuid_2},
                {"user1_uuid": uuid_2, "user2_uuid": uuid_1}
            ]
        })
        
        return result.deleted_count > 0

    @staticmethod
    async def get_users(skip: int, limit: int):
        db = Database.get_db()
        total = await db.users.count_documents({})
        cursor = db.users.find().skip(skip).limit(limit)
        users = [user async for user in cursor]
        return total, users

    @staticmethod
    async def get_user_by_uuid(uuid: str) -> Optional[dict]:
        db = Database.get_db()
        return await db.users.find_one({"uuid": uuid})

    @staticmethod
    async def get_user_by_email(email: str):
        db = Database.get_db()
        return await db.users.find_one({"email": email})

    @staticmethod
    async def update_user(uuid: str, user: UserBase):
        db = Database.get_db()
        user_dict = user.model_dump()
        user_dict["updated_at"] = datetime.now()
        result = await db.users.update_one(
            {"uuid": uuid},
            {"$set": user_dict}
        )
        if result.modified_count > 0:
            return await db.users.find_one({"uuid": uuid})
        return None

    @staticmethod
    async def patch_user(uuid: str, patch: UserPatch) -> Optional[dict]:
        db = Database.get_db()
        update_data = patch.model_dump(exclude_unset=True)
        
        if update_data:
            update_data["updated_at"] = datetime.now()
            result = await db.users.find_one_and_update(
                {"uuid": uuid},
                {"$set": update_data},
                return_document=True
            )
            return result
        return await UserService.get_user_by_uuid(uuid)

    @staticmethod
    async def delete_user(uuid: str) -> bool:
        db = Database.get_db()
        result = await db.users.delete_one({"uuid": uuid})
        return result.deleted_count > 0

    @staticmethod
    async def get_users_count() -> int:
        db = Database.get_db()
        return await db.users.count_documents({})

    @staticmethod
    async def get_active_users() -> List[dict]:
        db = Database.get_db()
        return [user async for user in db.users.find({"is_active": True})]

    @staticmethod
    async def get_users_with_filters(
        first: int = 10,
        after: Optional[str] = None,
        filter_params: Optional[Dict[str, Any]] = None,
        order_by: Optional[Dict[str, str]] = None,
        search_query: Optional[str] = None
    ) -> Tuple[List[dict], bool]:
        paginator = CursorPagination(
            collection_name='users',
            model_class=dict,
            field_mappings={
                'name_contains': 'name',
                'email_contains': 'email',
                'created_after': 'created_at',
                'created_before': 'created_at',
                'is_active': 'is_active'
            }
        )

        # Handle search query
        if search_query:
            filter_params = filter_params or {}
            filter_params['$or'] = [
                {'name_contains': search_query},
                {'email_contains': search_query}
            ]

        return await paginator.paginate(
            first=first,
            after=after,
            filter_params=filter_params,
            order_by=order_by
        )

    @staticmethod
    async def get_mutual_friends(
        user1_uuid: str,
        user2_uuid: str,
        limit: int = 10,
        cursor: Optional[str] = None
    ) -> Tuple[List[dict], bool]:
        # Get friends of both users
        user1_friends = set(friend['uuid'] for friend in await UserService.get_friends(user1_uuid))
        user2_friends = set(friend['uuid'] for friend in await UserService.get_friends(user2_uuid))
        
        # Find mutual friends
        mutual_friend_uuids = list(user1_friends.intersection(user2_friends))
        
        paginator = CursorPagination(
            collection_name='users',
            model_class=dict,
            field_mappings={}
        )
        
        return await paginator.paginate(
            first=limit,
            after=cursor,
            filter_params={'uuid': {'$in': mutual_friend_uuids}}
        )

    @staticmethod
    async def get_friendship(uuid: str) -> Optional[dict]:
        db = Database.get_db()
        return await db.friendships.find_one({'uuid': uuid})

    @staticmethod
    async def get_friendship_status(user1_uuid: str, user2_uuid: str) -> dict:
        db = Database.get_db()
        friendship = await db.friendships.find_one({
            '$or': [
                {'user1_uuid': user1_uuid, 'user2_uuid': user2_uuid},
                {'user1_uuid': user2_uuid, 'user2_uuid': user1_uuid}
            ]
        })
        
        if friendship:
            return {
                'are_friends': True,
                'friendship_date': friendship['created_at'],
                'friendship_uuid': friendship['uuid']
            }
        
        return {
            'are_friends': False,
            'friendship_date': None,
            'friendship_uuid': None
        }

    @staticmethod
    async def get_filtered_users_count(filter_params: Dict[str, Any] = None) -> int:
        """Get count of users matching the filter criteria"""
        try:
            db = Database.get_db()
            query = {}
            
            if filter_params:
                if 'name_contains' in filter_params:
                    query['name'] = {'$regex': filter_params['name_contains'], '$options': 'i'}
                if 'email_contains' in filter_params:
                    query['email'] = {'$regex': filter_params['email_contains'], '$options': 'i'}
                if 'is_active' in filter_params:
                    query['is_active'] = filter_params['is_active']
                if 'created_after' in filter_params:
                    query['created_at'] = {'$gt': filter_params['created_after']}
                if 'created_before' in filter_params:
                    query.setdefault('created_at', {})['$lt'] = filter_params['created_before']
                if 'referred_by' in filter_params:
                    query['referred_by'] = filter_params['referred_by']
            
            count = await db.users.count_documents(query)
            return int(count)  # Ensure we return an integer
        except Exception:
            return 0  # Return 0 if anything goes wrong
