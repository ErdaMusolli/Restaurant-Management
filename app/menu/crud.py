from sqlalchemy.orm import Session
from app.menu import models, schemas

def get_menu(db: Session, menu_id: int):
    return db.query(models.Menu).filter(models.Menu.id == menu_id).first()

def get_menus(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Menu).offset(skip).limit(limit).all()

def create_menu(db: Session, menu: schemas.MenuCreate):
    new_menu = models.Menu(**menu.dict())
    db.add(new_menu)
    db.commit()
    db.refresh(new_menu)
    return new_menu

def update_menu(db: Session, db_menu: models.Menu, updates: schemas.MenuUpdate):
    for key, value in updates.dict(exclude_unset=True).items():
        setattr(db_menu, key, value)
    db.commit()
    db.refresh(db_menu)
    return db_menu

def delete_menu(db: Session, menu_id: int):
    menu = db.query(models.Menu).filter(models.Menu.id == menu_id).first()
    if menu:
        db.delete(menu)
        db.commit()
    return menu

