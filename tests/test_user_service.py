import pytest
from services.user_service import UserService
from models import UserCreate, UserPatch
from datetime import datetime
from database import Database

@pytest.fixture(autouse=True)
async def clean_db():
    """Clean the database before each test"""
    db = Database.get_db()
    await db.users.delete_many({})

@pytest.mark.asyncio
async def test_create_user():
    """Test creating a new user"""
    user_data = UserCreate(
        email="newuser@example.com",
        name="New User",
        password="password123"
    )
    
    user = await UserService.create_user(user_data)
    
    assert user is not None
    assert user["email"] == "newuser@example.com"
    assert user["name"] == "New User"
    assert user["is_active"] is True
    assert "uuid" in user
    assert "referral_code" in user
    assert "password" not in user  # Password should not be returned
    assert isinstance(user["created_at"], datetime)
    assert isinstance(user["updated_at"], datetime)

@pytest.mark.asyncio
async def test_create_duplicate_email():
    """Test that creating a user with duplicate email raises an error"""
    user_data = UserCreate(
        email="duplicate@example.com",
        name="First User",
        password="password123"
    )
    
    # Create first user
    await UserService.create_user(user_data)
    
    # Try to create second user with same email
    duplicate_data = UserCreate(
        email="duplicate@example.com",
        name="Second User",
        password="password456"
    )
    
    with pytest.raises(ValueError, match="Email already exists"):
        await UserService.create_user(duplicate_data)

@pytest.mark.asyncio
async def test_get_user_by_uuid():
    """Test retrieving a user by UUID"""
    # Create a user first
    user_data = UserCreate(
        email="test@example.com",
        name="Test User",
        password="testpassword123"
    )
    created_user = await UserService.create_user(user_data)
    
    # Now try to get the user
    user = await UserService.get_user_by_uuid(created_user["uuid"])
    
    assert user is not None
    assert user["uuid"] == created_user["uuid"]
    assert user["email"] == created_user["email"]
    assert user["name"] == created_user["name"]

@pytest.mark.asyncio
async def test_get_nonexistent_user():
    """Test retrieving a non-existent user"""
    user = await UserService.get_user_by_uuid("nonexistent-uuid")
    assert user is None

@pytest.mark.asyncio
async def test_patch_user():
    """Test updating user information"""
    # Create a user first
    user_data = UserCreate(
        email="test@example.com",
        name="Test User",
        password="testpassword123"
    )
    created_user = await UserService.create_user(user_data)
    
    # Now patch the user
    patch_data = UserPatch(
        name="Updated Name",
        is_active=False
    )
    
    updated_user = await UserService.patch_user(created_user["uuid"], patch_data)
    
    assert updated_user is not None
    assert updated_user["name"] == "Updated Name"
    assert updated_user["is_active"] is False
    assert updated_user["email"] == created_user["email"]  # Email should not change
    assert updated_user["uuid"] == created_user["uuid"]  # UUID should not change
