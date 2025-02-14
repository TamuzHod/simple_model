import asyncio
import sys
import os
from faker import Faker
import random
from datetime import datetime
import uuid

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database
from models import UserCreate
from services.user_service import UserService

fake = Faker()

async def clear_database():
    db = Database.get_db()
    await db.users.delete_many({})
    await db.friendships.delete_many({})
    print("Database cleared")

async def create_random_users(num_users=10):
    users = []
    for _ in range(num_users):
        user_data = UserCreate(
            email=fake.email(),
            name=fake.name(),
            password=fake.password(length=12),
            is_active=random.choice([True, True, True, False])  # 75% chance of being active
        )
        user = await UserService.create_user(user_data)
        users.append(user)
        print(f"Created user: {user['name']} ({user['email']})")
    return users

async def create_friendships(users, num_friendships=8):
    db = Database.get_db()
    created = []
    
    while len(created) < num_friendships:
        user1, user2 = random.sample(users, 2)
        
        # Check if friendship already exists
        existing = await db.friendships.find_one({
            "$or": [
                {"user1_uuid": user1["uuid"], "user2_uuid": user2["uuid"]},
                {"user1_uuid": user2["uuid"], "user2_uuid": user1["uuid"]}
            ]
        })
        
        if not existing:
            friendship = {
                "uuid": str(uuid.uuid4()),
                "user1_uuid": user1["uuid"],
                "user2_uuid": user2["uuid"],
                "created_at": datetime.now()
            }
            await db.friendships.insert_one(friendship)
            created.append(friendship)
            print(f"Created friendship: {user1['name']} - {user2['name']}")
    
    return created

async def create_referrals(users, num_referrals=4):
    referrers = random.sample(users, num_referrals)
    
    for referrer in referrers:
        user_data = UserCreate(
            email=fake.email(),
            name=fake.name(),
            password=fake.password(length=12),
            referral_code=referrer["referral_code"]
        )
        new_user = await UserService.create_user(user_data)
        print(f"Created referral: {new_user['name']} <- {referrer['name']}")

async def main():
    await Database.connect_db()
    
    try:
        await clear_database()
        users = await create_random_users(10)
        await create_friendships(users, 8)
        await create_referrals(users, 4)
        
        print("\nSeeding completed!")
        print("Created:")
        print("- 10 random users")
        print("- 8 friendships")
        print("- 4 referrals")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await Database.close_db()

if __name__ == "__main__":
    asyncio.run(main())
