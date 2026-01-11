from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.restaurants.models import Restaurant
from app.auth.oauth2 import require_admin, require_manager,get_current_user
from .schemas import RestaurantCreate, RestaurantRead, RestaurantUpdate


router = APIRouter(prefix="/restaurants", tags=["Restaurants"])

@router.post("/", response_model=RestaurantRead, dependencies=[Depends(require_admin())])
async def create_restaurant(data: RestaurantCreate, db: AsyncSession = Depends(get_db)):
    restaurant = Restaurant(**data.dict())
    db.add(restaurant)
    await db.commit()
    await db.refresh(restaurant)
    return restaurant

@router.get("/", response_model=list[RestaurantRead])
async def get_all_restaurants(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Restaurant))
    return result.scalars().all()

@router.get("/me", response_model=RestaurantRead, dependencies=[Depends(require_manager())])
async def get_my_restaurant(
    current_user = Depends(require_manager()),
    db: AsyncSession = Depends(get_db)
):
    restaurant = await db.get(Restaurant, current_user.restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    return restaurant

@router.put("/me", response_model=RestaurantRead, dependencies=[Depends(require_manager())])
async def update_my_restaurant(
    data: RestaurantUpdate,
    current_user = Depends(require_manager()),
    db: AsyncSession = Depends(get_db)
):
    restaurant = await db.get(Restaurant, current_user.restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    for key, value in data.dict(exclude_unset=True).items():
        setattr(restaurant, key, value)
    
    await db.commit()
    await db.refresh(restaurant)
    return restaurant

@router.delete("/{restaurant_id}", dependencies=[Depends(require_admin())])
async def delete_restaurant(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    restaurant = await db.get(Restaurant, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    await db.delete(restaurant)
    await db.commit()
    return {"message": "Restaurant deleted successfully"}