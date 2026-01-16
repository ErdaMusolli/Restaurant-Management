import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.database import get_db
from app.users import crud, schemas
from app.auth.oauth2 import require_admin
from app.users.models import User

logger = logging.getLogger("app_logger")

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=schemas.UserRead, dependencies=[Depends(require_admin())])
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_email(db, user.email)
    if db_user:
        logger.warning(f"Attempted to create duplicate user email={user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = await crud.create_user(db, user)
    logger.info(f"Admin created user id={new_user.id}, email={new_user.email}")
    return new_user

@router.get("/", response_model=List[schemas.UserRead], dependencies=[Depends(require_admin())])
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    logger.info(f"Admin fetched list of users, total={len(users)}")
    return users

@router.patch("/{user_id}", response_model=schemas.UserRead, dependencies=[Depends(require_admin())])
async def update_user(user_id: int, updates: schemas.UserUpdate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_id(db, user_id)
    if not db_user:
        logger.warning(f"Attempted update on non-existent user id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = await crud.update_user(db, db_user, updates)
    logger.info(f"Admin updated user id={user_id}")
    return updated_user

@router.delete("/{user_id}", dependencies=[Depends(require_admin())])
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_id(db, user_id)
    if not db_user:
        logger.warning(f"Attempted delete on non-existent user id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    await crud.delete_user(db, db_user)
    logger.info(f"Admin deleted user id={user_id}")
    return {"detail": "User deleted successfully"}
