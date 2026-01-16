from fastapi import FastAPI
from app.database import engine, Base
from app.users.router import router as users_router
from app.auth.router import router as auth_router
from app.restaurants.router import router as restaurants_router
from app.orders.router import router as orders_router
from app.menu.router import router as menu_router
from app.dish.router import router as dish_router
from app.admin.router import router as admin_router
from app.cart.router import router as cart_router
from fastapi import Request
import logging
import time
from fastapi.security import OAuth2PasswordBearer
from prometheus_fastapi_instrumentator import Instrumentator



import asyncio


app = FastAPI(title="Restaurant Management Backend")

app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(restaurants_router, prefix="/api/v1/restaurants", tags=["Restaurants"])
app.include_router(orders_router, prefix="/api/v1/orders", tags=["Orders"])
app.include_router(cart_router, prefix="/api/v1/cart", tags=["Cart"])
app.include_router(menu_router, prefix="/api/v1/menus", tags=["Menus"])
app.include_router(dish_router, prefix="/api/v1/dishes", tags=["Dishes"])




async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


logger = logging.getLogger("app_logger")
logging.basicConfig(level=logging.INFO)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url} completed in {process_time:.2f}s with status {response.status_code}")
    return response

@app.on_event("startup")
async def on_startup():
    await init_models()

@app.get("/api/v1/test-db")
async def test_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(lambda x: None)
        return {"status": "connected"}
    except Exception as e:
        return {"status": "error", "details": str(e)}



instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)
