from datetime import datetime
import uuid
from typing import List, Tuple, Optional, Dict, Any
from models import UserCreate, UserBase, UserPatch
from database import Database
import secrets
from bson import ObjectId

class UserService:
    @staticmethod
    async def create_user(user: UserCreate) -> dict:
        db = Database.get_db()
        user_dict = user.model_dump()
        del user_dict["password"]  # In a real app, you'd hash the password
        
        # Generate unique referral code
        while True:
            referral_code = secrets.token_urlsafe(8)
            existing = await db.users.find_one({"referral_code": referral_code})
            if not existing:
                break
        
        # Handle referral
        if user.referral_code:
            referrer = await db.users.find_one({"referral_code": user.referral_code})
            if referrer:
                user_dict["referred_by"] = referrer["uuid"]
        
        # Add server-generated fields
        now = datetime.now()
        user_dict["uuid"] = str(uuid.uuid4())
        user_dict["created_at"] = now
        user_dict["updated_at"] = now
        user_dict["referral_code"] = referral_code
        
        await db.users.insert_one(user_dict)
        return await db.users.find_one({"uuid": user_dict["uuid"]})

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
    async def get_friends(user_uuid: str) -> List[dict]:
        db = Database.get_db()
        
        friendships = await db.friendships.find({
            "$or": [
                {"user1_uuid": user_uuid},
                {"user2_uuid": user_uuid}
            ]
        }).to_list(length=None)
        
        friend_uuids = []
        for friendship in friendships:
            friend_uuid = friendship["user2_uuid"] if friendship["user1_uuid"] == user_uuid \
                         else friendship["user1_uuid"]
            friend_uuids.append(friend_uuid)
        
        if not friend_uuids:
            return []
            
        return await db.users.find({"uuid": {"$in": friend_uuids}}).to_list(length=None)

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
    async def get_user_by_uuid(uuid: str):
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
    async def patch_user(uuid: str, user: UserPatch):
        db = Database.get_db()
        update_data = {
            k: v for k, v in user.model_dump().items() 
            if v is not None
        }
        if not update_data:
            return None
        
        update_data["updated_at"] = datetime.now()
        result = await db.users.update_one(
            {"uuid": uuid},
            {"$set": update_data}
        )
        if result.modified_count > 0:
            return await db.users.find_one({"uuid": uuid})
        return None

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
    async def get_users_with_cursor(
        limit: int,
        cursor: Optional[str] = None,
        filter_params: Optional[Dict[str, Any]] = None,
        order_by: Optional[Dict[str, str]] = None,
        search_query: Optional[str] = None
    ):
        db = Database.get_db()
        query = {}

        # Handle cursor-based pagination
        if cursor:
            cursor_obj = ObjectId(cursor)
            query['_id'] = {'$gt': cursor_obj}

        # Handle filtering
        if filter_params:
            if filter_params.get('name_contains'):
                query['name'] = {'$regex': filter_params['name_contains'], '$options': 'i'}
            if filter_params.get('email_contains'):
                query['email'] = {'$regex': filter_params['email_contains'], '$options': 'i'}
            if filter_params.get('is_active') is not None:
                query['is_active'] = filter_params['is_active']
            if filter_params.get('created_after'):
                query['created_at'] = {'$gt': filter_params['created_after']}
            if filter_params.get('created_before'):
                query.setdefault('created_at', {})['$lt'] = filter_params['created_before']

        # Handle search
        if search_query:
            query['$or'] = [
                {'name': {'$regex': search_query, '$options': 'i'}},
                {'email': {'$regex': search_query, '$options': 'i'}}
            ]

        # Handle sorting
        sort_params = [('_id', 1)]  # default sorting
        if order_by:
            sort_params = [(order_by['field'], 1 if order_by['direction'] == 'ASC' else -1)]

        # Execute query
        cursor = db.users.find(query).sort(sort_params).limit(limit + 1)
        users = await cursor.to_list(length=limit + 1)

        # Check if there are more results
        has_next_page = len(users) > limit
        if has_next_page:
            users = users[:-1]

        return users, has_next_page

    @staticmethod
    async def get_mutual_friends(user1_uuid: str, user2_uuid: str, limit: int, cursor: Optional[str] = None):
        db = Database.get_db()
        
        # Get friends of both users
        user1_friends = set(friend['uuid'] for friend in await UserService.get_friends(user1_uuid))
        user2_friends = set(friend['uuid'] for friend in await UserService.get_friends(user2_uuid))
        
        # Find mutual friends
        mutual_friend_uuids = list(user1_friends.intersection(user2_friends))
        
        query = {'uuid': {'$in': mutual_friend_uuids}}
        if cursor:
            query['_id'] = {'$gt': ObjectId(cursor)}
            
        cursor = db.users.find(query).limit(limit + 1)
        users = await cursor.to_list(length=limit + 1)
        
        has_next_page = len(users) > limit
        if has_next_page:
            users = users[:-1]
            
        return users, has_next_page

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
