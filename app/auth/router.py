from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.utils.security import create_access_token
from .crud import create_refresh_token, get_refresh_token, delete_refresh_token
from app.users.crud import get_user_by_email, get_user_by_id
from app.utils.security import verify_password


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token({"sub": user.id})
    refresh_token = await create_refresh_token(db, user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token.token,
        "token_type": "bearer"
    }

@router.post("/refresh")
async def refresh_token_endpoint(refresh_token: str, db: AsyncSession = Depends(get_db)):
    token_obj = await get_refresh_token(db, refresh_token)
    if not token_obj:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = await get_user_by_id(db, token_obj.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await delete_refresh_token(db, token_obj)

    new_access_token = create_access_token({"sub": user.id})
    new_refresh_token = await create_refresh_token(db, user.id)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token.token,
        "token_type": "bearer"
    }