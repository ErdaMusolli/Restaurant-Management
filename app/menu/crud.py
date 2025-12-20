from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.menu import models, schemas

async def get_menus(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Menu).offset(skip).limit(limit))
    return result.scalars().all()

async def get_menu(db: AsyncSession, menu_id: int):
    result = await db.execute(select(models.Menu).where(models.Menu.id == menu_id))
    return result.scalars().first()

async def create_menu(db: AsyncSession, menu: schemas.MenuCreate):
    new_menu = models.Menu(**menu.dict())
    db.add(new_menu)
    await db.commit()
    await db.refresh(new_menu)
    return new_menu

async def update_menu(db: AsyncSession, db_menu: models.Menu, updates: schemas.MenuUpdate):
    for key, value in updates.dict(exclude_unset=True).items():
        setattr(db_menu, key, value)
    await db.commit()
    await db.refresh(db_menu)
    return db_menu

async def delete_menu(db: AsyncSession, menu_id: int):
    menu = await get_menu(db, menu_id)
    if menu:
        await db.delete(menu)
        await db.commit()
    return menu
