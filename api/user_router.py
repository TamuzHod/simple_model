from fastapi import APIRouter, HTTPException, Query, status
from models import (
    User, UserCreate, UserBase, UserPatch, PaginatedUsers,
    Friendship, ReferralStats
)
from services.user_service import UserService
from typing import List, Optional
from fastapi.responses import Response
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    try:
        created_user = await UserService.create_user(user)
        return User(**created_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        if "duplicate key error" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@router.get("/", response_model=PaginatedUsers, status_code=status.HTTP_200_OK)
async def read_users(
    first: int = Query(default=10, ge=1, le=100, description="Number of items to fetch"),
    after: Optional[str] = Query(None, description="Cursor for pagination"),
    active: Optional[bool] = Query(None, description="Filter by active status")
):
    try:
        filter_params = {"is_active": active} if active is not None else None
        users, has_next_page = await UserService.get_users_with_filters(
            first=first,
            after=after,
            filter_params=filter_params
        )
        
        return PaginatedUsers(
            items=[User(**user) for user in users],
            cursor=users[-1]["_id"] if users else None,
            has_next_page=has_next_page,
            total=await UserService.get_users_count()  # Keep total count for UI purposes
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.head("/", status_code=status.HTTP_200_OK)
async def get_users_count():
    try:
        count = await UserService.get_users_count()
        return Response(
            content=None,
            headers={"X-Total-Count": str(count)}
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get users count"
        )

@router.get("/email/{email}", response_model=User, status_code=status.HTTP_200_OK)
async def get_user_by_email(email: str):
    try:
        user = await UserService.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return User(**user)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )

@router.get("/{uuid}", response_model=User, status_code=status.HTTP_200_OK)
async def read_user(uuid: str):
    try:
        user = await UserService.get_user_by_uuid(uuid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return User(**user)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )

@router.put("/{uuid}", response_model=User, status_code=status.HTTP_200_OK)
async def update_user(uuid: str, user: UserBase):
    try:
        updated_user = await UserService.update_user(uuid, user)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return User(**updated_user)
    except HTTPException:
        raise
    except Exception as e:
        if "duplicate key error" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )

@router.patch("/{uuid}", response_model=User, status_code=status.HTTP_200_OK)
async def patch_user(uuid: str, user: UserPatch):
    try:
        updated_user = await UserService.patch_user(uuid, user)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return User(**updated_user)
    except HTTPException:
        raise
    except Exception as e:
        if "duplicate key error" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )

@router.delete("/{uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(uuid: str):
    try:
        if not await UserService.delete_user(uuid):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return None
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )

# Friendship endpoints
@router.post("/{uuid_1}/friends/{uuid_2}", response_model=Friendship, status_code=status.HTTP_201_CREATED)
async def create_friendship(uuid_1: str, uuid_2: str):
    """Create a friendship between two users"""
    try:
        friendship = await UserService.send_friend_request(uuid_1, uuid_2)
        return Friendship(**friendship)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create friendship {e}"
        )

@router.get("/{user_uuid}/friends", response_model=List[User], status_code=status.HTTP_200_OK)
async def get_user_friends(user_uuid: str):
    """Get all friends of a user"""
    try:
        user = await UserService.get_user_by_uuid(user_uuid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        friends = await UserService.get_friends(user_uuid)
        return [User(**friend) for friend in friends]
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get friends"
        )

@router.delete("/{uuid_1}/friends/{uuid_2}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_friendship(uuid_1: str, uuid_2: str):
    """Remove a friendship between two users"""
    try:
        logger.info(f"Attempting to remove friendship between {uuid_1} and {uuid_2}")
        result = await UserService.remove_friend(uuid_1, uuid_2)
        if not result:
            logger.info("Friendship not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Friendship not found"
            )
        logger.info("Friendship successfully removed")
        return {"friendship_uuid": result}
    except ValueError as e:
        logger.error(f"ValueError in remove_friendship: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in remove_friendship: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove friendship"
        )

# Referral endpoints
@router.get("/{user_uuid}/referrals", response_model=ReferralStats)
async def get_referral_stats(user_uuid: str):
    """Get user's referral statistics"""
    try:
        user = await UserService.get_user_by_uuid(user_uuid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        total, referred_users = await UserService.get_referral_stats(user_uuid)
        return ReferralStats(
            total_referrals=total,
            successful_referrals=[User(**user) for user in referred_users]
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get referral stats"
        )

@router.get("/{user_uuid}/referral-code")
async def get_referral_code(user_uuid: str):
    """Get user's referral code"""
    try:
        user = await UserService.get_user_by_uuid(user_uuid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"referral_code": user["referral_code"]}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get referral code"
        )
