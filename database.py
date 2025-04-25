import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Database:
    client: Optional[AsyncIOMotorClient] = None

    @classmethod
    async def connect_db(cls):
        # Build MongoDB connection string based on environment variables
        user = os.environ.get('MONGODB_USER', '')
        password = os.environ.get('MONGODB_PASSWORD', '')
        host = os.environ.get('MONGODB_HOST', 'localhost')
        port = os.environ.get('MONGODB_PORT', '27017')

        # Create connection string with or without authentication
        if user and password:
            connection_string = f"mongodb://{user}:{password}@{host}:{port}"
        else:
            connection_string = f"mongodb://{host}:{port}"

        cls.client = AsyncIOMotorClient(connection_string)
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
