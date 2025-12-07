from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.restaurants.models import Restaurant
from app.restaurants.schemas import RestaurantCreate, RestaurantUpdate

async def create_restaurant(db: AsyncSession, restaurant: RestaurantCreate):
    db_restaurant = Restaurant(**restaurant.dict())
    db.add(db_restaurant)
    await db.commit()
    await db.refresh(db_restaurant)
    return db_restaurant

async def get_restaurant_by_id(db: AsyncSession, restaurant_id: int):
    result = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
    return result.scalars().first()

async def update_restaurant(db: AsyncSession, db_restaurant: Restaurant, updates: RestaurantUpdate):
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(db_restaurant, field, value)
    db.add(db_restaurant)
    await db.commit()
    await db.refresh(db_restaurant)
    return db_restaurant

async def delete_restaurant(db: AsyncSession, db_restaurant: Restaurant):
    await db.delete(db_restaurant)
    await db.commit()
    return db_restaurant
    
async def list_restaurants(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Restaurant).offset(skip).limit(limit))
    return result.scalars().all()
