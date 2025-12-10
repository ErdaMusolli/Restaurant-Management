from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.dish import crud, schemas

router = APIRouter(tags=["Dish"])

@router.get("/", response_model=list[schemas.DishOut])
def get_all(db: Session = Depends(get_db)):
    return crud.get_dishes(db)

@router.get("/{dish_id}", response_model=schemas.DishOut)
def get_one(dish_id: int, db: Session = Depends(get_db)):
    dish = crud.get_dish(db, dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    return dish

@router.post("/", response_model=schemas.DishOut)
def create(dish: schemas.DishCreate, db: Session = Depends(get_db)):
    return crud.create_dish(db, dish)

@router.put("/{dish_id}", response_model=schemas.DishOut)
def update(dish_id: int, updates: schemas.DishUpdate, db: Session = Depends(get_db)):
    db_dish = crud.get_dish(db, dish_id)
    if not db_dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    return crud.update_dish(db, db_dish, updates)

@router.delete("/{dish_id}")
def delete(dish_id: int, db: Session = Depends(get_db)):
    dish = crud.delete_dish(db, dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    return {"deleted": True}
