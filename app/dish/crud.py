from sqlalchemy.orm import Session
from app.dish import models, schemas

def get_dish(db: Session, dish_id: int):
    return db.query(models.Dish).filter(models.Dish.id == dish_id).first()

def get_dishes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Dish).offset(skip).limit(limit).all()

def create_dish(db: Session, dish: schemas.DishCreate):
    new_dish = models.Dish(**dish.dict())
    db.add(new_dish)
    db.commit()
    db.refresh(new_dish)
    return new_dish

def update_dish(db: Session, db_dish: models.Dish, updates: schemas.DishUpdate):
    for key, value in updates.dict(exclude_unset=True).items():
        setattr(db_dish, key, value)
    db.commit()
    db.refresh(db_dish)
    return db_dish

def delete_dish(db: Session, dish_id: int):
    dish = db.query(models.Dish).filter(models.Dish.id == dish_id).first()
    if dish:
        db.delete(dish)
        db.commit()
    return dish
