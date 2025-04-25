import pytest
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict
from database import Database

# Remove the event_loop fixture since pytest-asyncio provides it
@pytest.fixture(autouse=True)
async def setup_test_database():
    """Setup a test database connection before each test and cleanup after."""
    # Use a test database

    load_dotenv()

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

    Database.client = AsyncIOMotorClient(connection_string)
    Database.client.get_database("test_user_db")

    # Setup indexes
    db = Database.get_db()
    await db.users.create_index("uuid", unique=True)
    await db.users.create_index("email", unique=True)
    await db.users.create_index("referral_code", unique=True)

    yield

    # Cleanup after test
    await Database.client.drop_database("test_user_db")
    Database.client.close()

@pytest.fixture
async def sample_user() -> Dict:
    """Create a sample user for testing."""
    from services.user_service import UserService
    from models import UserCreate

    user_data = UserCreate(
        email="test@example.com",
        name="Test User",
        password="testpassword123"
    )

    user = await UserService.create_user(user_data)
    return user
