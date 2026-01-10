from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.users.crud import get_user_by_id
from app.restaurants.crud import get_restaurant_by_id
from app.auth.oauth2 import require_admin
from .schemas import AssignManager


router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/assign-manager")
async def assign_manager(
    data: AssignManager,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin())  
):
    manager = await get_user_by_id(db, data.manager_id)
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")
    if manager.role != "manager":
        raise HTTPException(status_code=400, detail="User is not a manager")
    
    restaurant = await get_restaurant_by_id(db, data.restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    manager.restaurant_id = restaurant.id
    await db.commit()
    await db.refresh(manager)
    
    return {"detail": f"Manager {manager.full_name} assigned to restaurant {restaurant.name}"}