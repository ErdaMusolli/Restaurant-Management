from fastapi import FastAPI
from app.database import engine, Base
from app.users.router import router as users_router
import asyncio

app = FastAPI(title="Restaurant Management Backend")

app.include_router(users_router, prefix="/users")

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def on_startup():
    await init_models()

@app.get("/test-db")
async def test_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(lambda x: None)
        return {"status": "connected"}
    except Exception as e:
        return {"status": "error", "details": str(e)} 

from menu.router import router as menu_router
from dish.router import router as dish_router



app.include_router(menu_router, prefix="/menus", tags=["Menus"])
app.include_router(dish_router, prefix="/dishes", tags=["Dishes"])


