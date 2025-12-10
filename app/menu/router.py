from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.menu import crud, schemas

router = APIRouter(tags=["Menu"])

@router.get("/", response_model=list[schemas.MenuOut])
def get_all(db: Session = Depends(get_db)):
    return crud.get_menus(db)

@router.get("/{menu_id}", response_model=schemas.MenuOut)
def get_one(menu_id: int, db: Session = Depends(get_db)):
    menu = crud.get_menu(db, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    return menu

@router.post("/", response_model=schemas.MenuOut)
def create(menu: schemas.MenuCreate, db: Session = Depends(get_db)):
    return crud.create_menu(db, menu)

@router.put("/{menu_id}", response_model=schemas.MenuOut)
def update(menu_id: int, updates: schemas.MenuUpdate, db: Session = Depends(get_db)):
    db_menu = crud.get_menu(db, menu_id)
    if not db_menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    return crud.update_menu(db, db_menu, updates)

@router.delete("/{menu_id}")
def delete(menu_id: int, db: Session = Depends(get_db)):
    menu = crud.delete_menu(db, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    return {"deleted": True}

