from datetime import datetime
import uuid
from models import UserCreate, UserBase, UserPatch
from database import Database
from typing import List

class UserService:
    @staticmethod
    async def create_user(user: UserCreate):
        user_dict = user.model_dump()
        del user_dict["password"]  # In a real app, you'd hash the password
        
        # Add server-generated fields
        user_dict["uuid"] = str(uuid.uuid4())
        user_dict["created_at"] = datetime.now()
        
        db = Database.get_db()
        await db.users.insert_one(user_dict)
        return await db.users.find_one({"uuid": user_dict["uuid"]})

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