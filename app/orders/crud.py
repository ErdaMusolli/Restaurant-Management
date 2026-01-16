from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from .models import Order, OrderItem
from .schemas import OrderCreate, OrderUpdate
from app.dish.models import Dish
from app.cart.models import Cart, CartItem


async def create_order(
    db,
    order,
    user_id: int
):
    total_price = 0.0

    for item in order.items:
        dish = await db.get(Dish, item.dish_id)
        if not dish:
            raise HTTPException(status_code=404, detail=f"Dish with id {item.dish_id} not found")

        total_price += dish.price * item.quantity

    db_order = Order(
        user_id=user_id,
        restaurant_id=order.restaurant_id,
        total_price=total_price,
        status="Pending"
    )

    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)

    for item in order.items:
        dish = await db.get(Dish, item.dish_id)

        db_item = OrderItem(
            order_id=db_order.id,
            dish_id=dish.id,
            quantity=item.quantity,
            price=dish.price
        )
        db.add(db_item)

    await db.commit()

    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.restaurant),
            selectinload(Order.items)
        )
        .where(Order.id == db_order.id)
    )

    return result.scalars().first()

async def get_order_by_id(db: AsyncSession, order_id: int):
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.restaurant),
            selectinload(Order.items)
        )
        .where(Order.id == order_id)
    )
    return result.scalars().first()


async def get_orders_by_user(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.restaurant),
            selectinload(Order.items)
        )
        .where(Order.user_id == user_id)
    )
    return result.scalars().all()


async def get_orders_by_restaurant(db: AsyncSession, restaurant_id: int):
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.restaurant),
            selectinload(Order.items)
        )
        .where(Order.restaurant_id == restaurant_id)
    )
    return result.scalars().all()


async def get_all_orders(db: AsyncSession):
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.restaurant),
            selectinload(Order.items)
        )
    )
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

async def checkout_cart(db: AsyncSession, user_id: int):

    result = await db.execute(select(Cart).where(Cart.user_id == user_id))
    cart = result.scalar_one_or_none()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart is empty")

    items = (await db.execute(select(CartItem).where(CartItem.cart_id == cart.id))).scalars().all()
    if not items:
        raise HTTPException(status_code=404, detail="Cart is empty")

    first_dish = await db.get(Dish, items[0].dish_id)
    restaurant_id = first_dish.restaurant_id

    db_order = Order(user_id=user_id, restaurant_id=restaurant_id, total_price=0, status="Pending")
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)

    total_price = 0
    for item in items:
        dish = await db.get(Dish, item.dish_id)
        db_item = OrderItem(
            order_id=db_order.id,
            dish_id=dish.id,
            quantity=item.quantity,
            price=dish.price
        )
        db.add(db_item)
        total_price += dish.price * item.quantity

    db_order.total_price = total_price
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)

    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.restaurant),
            selectinload(Order.items)
        )
        .where(Order.id == db_order.id)
    )
    db_order = result.scalars().first()

    await db.execute(CartItem.__table__.delete().where(CartItem.cart_id == cart.id))
    await db.commit()

    return db_order