from typing import List

from config import AVAILABLE_PLATFORMS
from fastapi import APIRouter, Depends, HTTPException
from models import PlatformAccount, PlatformAccountCreate
from routes.dependencies import get_db

router = APIRouter(prefix="/api/platforms", tags=["platforms"])


# Use dependency-injected database (from app.state) via routes.dependencies.get_db


# Create Platform Account
@router.post("/accounts", response_model=PlatformAccount)
async def create_platform_account(
    account: PlatformAccountCreate, database=Depends(get_db)
):
    account_dict = account.dict()
    account_obj = PlatformAccount(**account_dict)
    await database.platform_accounts.insert_one(account_obj.dict())
    return account_obj


# Get All Platform Accounts
@router.get("/accounts", response_model=List[PlatformAccount])
async def get_platform_accounts(platform: str = None, database=Depends(get_db)):
    query = {}
    if platform:
        query["platform"] = platform
    accounts = await database.platform_accounts.find(query).to_list(1000)
    return [PlatformAccount(**acc) for acc in accounts]


# Get Platform Account by ID
@router.get("/accounts/{account_id}", response_model=PlatformAccount)
async def get_platform_account(account_id: str, database=Depends(get_db)):
    account = await database.platform_accounts.find_one({"id": account_id})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return PlatformAccount(**account)


# Update Platform Account Status
@router.put("/accounts/{account_id}/status")
async def update_account_status(account_id: str, status: str, database=Depends(get_db)):
    account = await database.platform_accounts.find_one({"id": account_id})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    await database.platform_accounts.update_one(
        {"id": account_id}, {"$set": {"status": status}}
    )

    updated_account = await database.platform_accounts.find_one({"id": account_id})
    return PlatformAccount(**updated_account)


# Delete Platform Account
@router.delete("/accounts/{account_id}")
async def delete_platform_account(account_id: str, database=Depends(get_db)):
    result = await database.platform_accounts.delete_one({"id": account_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"message": "Account deleted successfully"}


# Get Available Platforms
@router.get("/available")
async def get_available_platforms():
    """
    Get list of all available platforms for cross-posting.
    Platform definitions are centrally managed in config.platforms module.
    """
    return AVAILABLE_PLATFORMS
