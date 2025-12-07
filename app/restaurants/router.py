from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.restaurants import crud, schemas

router = APIRouter()

@router.post("/", response_model=schemas.RestaurantRead)
async def create_restaurant(restaurant: schemas.RestaurantCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_restaurant(db, restaurant)

@router.get("/{restaurant_id}", response_model=schemas.RestaurantRead)
async def get_restaurant(restaurant_id: int, db: AsyncSession = Depends(get_db)):
    restaurant = await crud.get_restaurant_by_id(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant

@router.get("/", response_model=list[schemas.RestaurantRead])
async def list_restaurants(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.list_restaurants(db)

@router.put("/{restaurant_id}", response_model=schemas.RestaurantRead)
async def update_restaurant(restaurant_id: int, updates: schemas.RestaurantUpdate, db: AsyncSession = Depends(get_db)):
    db_restaurant = await crud.get_restaurant_by_id(db, restaurant_id)
    if not db_restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return await crud.update_restaurant(db, db_restaurant, updates)

@router.delete("/{restaurant_id}", response_model=schemas.RestaurantRead)
async def delete_restaurant(restaurant_id: int, db: AsyncSession = Depends(get_db)):
    db_restaurant = await crud.get_restaurant_by_id(db, restaurant_id)
    if not db_restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return await crud.delete_restaurant(db, db_restaurant)