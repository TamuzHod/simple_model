from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

class Database:
    client: Optional[AsyncIOMotorClient] = None
    
    @classmethod
    async def connect_db(cls):
        cls.client = AsyncIOMotorClient("mongodb://localhost:27017")
        db = cls.client.user_db
        
        # User indexes
        await db.users.create_index("uuid", unique=True)
        await db.users.create_index("email", unique=True)
        await db.users.create_index("referral_code", unique=True)
        
        # Friendship indexes
        await db.friendships.create_index("uuid", unique=True)
        # Compound index for finding existing friendships
        await db.friendships.create_index([
            ("user1_uuid", 1),
            ("user2_uuid", 1)
        ], unique=True)
        
    @classmethod
    async def close_db(cls):
        if cls.client is not None:
            cls.client.close()
            
    @classmethod
    def get_db(cls):
        if cls.client is None:
            raise Exception("Database not initialized")
        return cls.client.user_db  # user_db is our database name
