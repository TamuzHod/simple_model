from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

class Database:
    client: Optional[AsyncIOMotorClient] = None
    
    @classmethod
    async def connect_db(cls):
        # Using localhost MongoDB for development
        cls.client = AsyncIOMotorClient("mongodb://localhost:27017")
        # Create unique indexes
        await cls.client.user_db.users.create_index("uuid", unique=True)
        await cls.client.user_db.users.create_index("email", unique=True)
        
    @classmethod
    async def close_db(cls):
        if cls.client is not None:
            cls.client.close()
            
    @classmethod
    def get_db(cls):
        if cls.client is None:
            raise Exception("Database not initialized")
        return cls.client.user_db  # user_db is our database name
