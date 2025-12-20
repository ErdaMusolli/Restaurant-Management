from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dish import crud, schemas

router = APIRouter(tags=["Dishes"], prefix="/dishes")

@router.get("/", response_model=list[schemas.DishOut])
async def get_all(db: AsyncSession = Depends(get_db)):
    return await crud.get_dishes(db)

@router.get("/{dish_id}", response_model=schemas.DishOut)
async def get_one(dish_id: int, db: AsyncSession = Depends(get_db)):
    dish = await crud.get_dish(db, dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    return dish

@router.post("/", response_model=schemas.DishOut)
async def create(dish: schemas.DishCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_dish(db, dish)

@router.put("/{dish_id}", response_model=schemas.DishOut)
async def update(dish_id: int, updates: schemas.DishUpdate, db: AsyncSession = Depends(get_db)):
    db_dish = await crud.get_dish(db, dish_id)
    if not db_dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    return await crud.update_dish(db, db_dish, updates)

@router.delete("/{dish_id}")
async def delete(dish_id: int, db: AsyncSession = Depends(get_db)):
    dish = await crud.delete_dish(db, dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    return {"deleted": True}
