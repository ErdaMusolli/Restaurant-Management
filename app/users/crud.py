from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate
from app.utils.security import get_password_hash


async def create_user(db: AsyncSession, user: UserCreate):
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=get_password_hash(user.password)
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()
    
async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def update_user(db: AsyncSession, db_user: User, updates: UserUpdate):
    if updates.full_name:
        db_user.full_name = updates.full_name
    if updates.password:
        db_user.hashed_password = get_password_hash(updates.password)
    if updates.is_active is not None:
        db_user.is_active = updates.is_active
    if updates.role:
        db_user.role = updates.role

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def delete_user(db: AsyncSession, db_user: User):
    await db.delete(db_user)
    await db.commit()
    return db_user