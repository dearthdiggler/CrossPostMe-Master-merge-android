from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from models import User
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from routes.dependencies import get_db
from services.auth import create_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
async def register(req: RegisterRequest, database=Depends(get_db)):
    existing = await database.users.find_one({"email": req.email})
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    # Server-side password validation: min 8 chars, must include letter and number
    import re

    if (
        len(req.password) < 8
        or not re.search(r"[A-Za-z]", req.password)
        or not re.search(r"\d", req.password)
    ):
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters and include letters and numbers",
        )
    hashed = pwd_context.hash(req.password)
    user = User(email=req.email, hashed_password=hashed, created_at=datetime.utcnow())
    res = await database.users.insert_one(user.dict())
    # Ensure consistent id: use the inserted_id if present
    uid = None
    if res and getattr(res, "inserted_id", None):
        uid = str(res.inserted_id)
    else:
        uid = user.id
    token = create_token(uid)
    return {"access_token": token}


@router.post("/login")
async def login(req: LoginRequest, database=Depends(get_db)):
    existing = await database.users.find_one({"email": req.email})
    if not existing:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not pwd_context.verify(req.password, existing.get("hashed_password")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # existing may have _id (ObjectId) or id field; prefer _id
    uid = existing.get("id") or existing.get("_id")
    if uid is not None:
        uid = str(uid)
    token = create_token(uid)
    return {"access_token": token}
