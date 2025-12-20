from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select 
from typing import List
from app.database import get_db
from app.users import crud, schemas
from app.auth.oauth2 import require_role
from app.users.models import User


router = APIRouter()

@router.post("/", response_model=schemas.UserRead)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud.create_user(db, user)

@router.get("/", response_model=list[schemas.UserRead])
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(crud.User))
    return result.scalars().all()

@router.patch("/{user_id}", response_model=schemas.UserRead, dependencies=[Depends(require_role("admin"))])
async def update_user(user_id: int, updates: schemas.UserUpdate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return await crud.update_user(db, db_user, updates)

@router.delete("/{user_id}", dependencies=[Depends(require_role("admin"))])
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    await crud.delete_user(db, db_user)
    return {"detail": "User deleted successfully"}