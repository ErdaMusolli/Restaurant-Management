from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from jose import jwt
from app.restaurants import schemas
from app.auth.oauth2 import get_current_user, require_admin, require_manager
from app.database import get_db
from app.users.schemas import UserCreate
from .schemas import UserRegister
from app.users.crud import get_user_by_email, get_user_by_id, create_user
from .crud import create_refresh_token, get_refresh_token, delete_refresh_token
from app.utils.security import verify_password, SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/auth", tags=["Authentication"])

def create_access_token(data: dict, expires_minutes: int = 15):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,  
    db: AsyncSession = Depends(get_db)
):
    db_user = await get_user_by_email(db, user_data.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user_create_data = UserCreate(
        email=user_data.email,
        full_name=user_data.full_name,
        password=user_data.password,
        role="user" 
    )
    
    user = await create_user(db, user_create_data)
    
    access_token = create_access_token({
        "sub": str(user.id),
        "role": user.role
    })
    refresh_token = await create_refresh_token(db, user.id)
    
    return {
        "message": "User registered successfully",
        "user_id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "access_token": access_token,
        "refresh_token": refresh_token.token,
        "token_type": "bearer"
    }

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token({
    "sub": str(user.id),   
    "role": user.role
})
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
    new_access_token = create_access_token({"sub": str(user.id), "role": user.role})
    new_refresh_token = await create_refresh_token(db, user.id)
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token.token,
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout(refresh_token: str, db: AsyncSession = Depends(get_db)):
    token_obj = await get_refresh_token(db, refresh_token)
    if token_obj:
        await delete_refresh_token(db, token_obj)
    return {"detail": "Logged out successfully"}
 