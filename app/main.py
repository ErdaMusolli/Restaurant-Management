from fastapi import FastAPI
from app.database import engine, Base
from app.users.models import User
import asyncio
from app.users.router import router as users_router


app = FastAPI(title="Restaurant Management Backend")
app.include_router(users_router, prefix="/users", tags=["Users"])

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
