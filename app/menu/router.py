from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.menu import crud, schemas

router = APIRouter(tags=["Menu"], prefix="/menus")

@router.get("/", response_model=list[schemas.MenuOut])
async def get_all(db: AsyncSession = Depends(get_db)):
    return await crud.get_menus(db)

@router.get("/{menu_id}", response_model=schemas.MenuOut)
async def get_one(menu_id: int, db: AsyncSession = Depends(get_db)):
    menu = await crud.get_menu(db, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    return menu

@router.post("/", response_model=schemas.MenuOut)
async def create(menu: schemas.MenuCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_menu(db, menu)

@router.put("/{menu_id}", response_model=schemas.MenuOut)
async def update(menu_id: int, updates: schemas.MenuUpdate, db: AsyncSession = Depends(get_db)):
    db_menu = await crud.get_menu(db, menu_id)
    if not db_menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    return await crud.update_menu(db, db_menu, updates)

@router.delete("/{menu_id}")
async def delete(menu_id: int, db: AsyncSession = Depends(get_db)):
    menu = await crud.delete_menu(db, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    return {"deleted": True}
