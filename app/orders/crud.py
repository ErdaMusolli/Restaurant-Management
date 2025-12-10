from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import Order
from .schemas import OrderCreate, OrderUpdate

async def create_order(db: AsyncSession, order: OrderCreate):
    db_order = Order(
        user_id=order.user_id,
        restaurant_id=order.restaurant_id,
        total_price=order.total_price,
        status=order.status
    )
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    return db_order

async def get_order_by_id(db: AsyncSession, order_id: int):
    result = await db.execute(select(Order).where(Order.id == order_id))
    return result.scalars().first()

async def get_orders_by_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(Order).where(Order.user_id == user_id))
    return result.scalars().all()

async def get_all_orders(db: AsyncSession):
    result = await db.execute(select(Order))
    return result.scalars().all()

async def update_order_status(db: AsyncSession, db_order: Order, status_update: OrderUpdate):
    db_order.status = status_update.status
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    return db_order

async def delete_order(db: AsyncSession, db_order: Order):
    await db.delete(db_order)
    await db.commit()
    return db_order
