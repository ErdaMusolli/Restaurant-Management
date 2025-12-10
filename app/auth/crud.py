from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import RefreshToken
import secrets

async def create_refresh_token(db: AsyncSession, user_id: int):
    token_str = secrets.token_urlsafe(32)
    token = RefreshToken(token=token_str, user_id=user_id)
    db.add(token)
    await db.commit()
    await db.refresh(token)
    return token

async def get_refresh_token(db: AsyncSession, token_str: str):
    result = await db.execute(select(RefreshToken).where(RefreshToken.token == token_str))
    return result.scalars().first()

async def delete_refresh_token(db: AsyncSession, token_obj: RefreshToken):
    await db.delete(token_obj)
    await db.commit()
