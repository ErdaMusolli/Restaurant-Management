from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.dish import models, schemas

async def get_dish(db: AsyncSession, dish_id: int):
    result = await db.execute(select(models.Dish).where(models.Dish.id == dish_id))
    return result.scalars().first()

async def get_dishes(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Dish).offset(skip).limit(limit))
    return result.scalars().all()

async def create_dish(db: AsyncSession, dish: schemas.DishCreate):
    new_dish = models.Dish(**dish.dict())
    db.add(new_dish)
    await db.commit()
    await db.refresh(new_dish)
    return new_dish

async def update_dish(db: AsyncSession, db_dish: models.Dish, updates: schemas.DishUpdate):
    for key, value in updates.dict(exclude_unset=True).items():
        setattr(db_dish, key, value)
    await db.commit()
    await db.refresh(db_dish)
    return db_dish

async def delete_dish(db: AsyncSession, dish_id: int):
    dish = await get_dish(db, dish_id)
    if dish:
        await db.delete(dish)
        await db.commit()
    return dish
