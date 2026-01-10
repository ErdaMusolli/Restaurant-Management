from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.users.crud import get_user_by_id
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user_by_id(db, int(user_id))
    if not user:
        raise credentials_exception
    return user

def require_admin():
    async def checker(current_user = Depends(get_current_user)):
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Only admin allowed")
        return current_user
    return checker

def require_manager():
    async def checker(current_user = Depends(get_current_user)):
        if current_user.role != "manager":
            raise HTTPException(status_code=403, detail="Only manager allowed")
        if not current_user.restaurant_id:
            raise HTTPException(status_code=403, detail="Manager not assigned to a restaurant")
        return current_user
    return checker
