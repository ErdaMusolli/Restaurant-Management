from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.cart.models import Cart, CartItem
from app.cart.schemas import CartResponse
from app.auth.router import get_current_user
from app.dish.models import Dish
from app.orders.schemas import OrderRead
from app.orders import crud as order_crud
import logging

router = APIRouter(prefix="/cart", tags=["Cart"])
logger = logging.getLogger("app_logger")

async def get_or_create_cart(db: AsyncSession, user_id: int, restaurant_id: int):
    result = await db.execute(select(Cart).where(Cart.user_id == user_id))
    cart = result.scalars().first()
    if not cart:
        cart = Cart(user_id=user_id, restaurant_id=restaurant_id)
        db.add(cart)
        try:
            await db.commit()
            await db.refresh(cart)
        except IntegrityError as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=f"Cannot create cart: {str(e)}")
    return cart

@router.post("/add", response_model=CartResponse)
async def add_to_cart(dish_id: int, quantity: int = 1, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    dish = await db.get(Dish, dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    if not dish.restaurant_id:
        raise HTTPException(status_code=400, detail="Dish has no restaurant assigned")
    cart = await get_or_create_cart(db=db, user_id=user.id, restaurant_id=dish.restaurant_id)
    result = await db.execute(select(CartItem).where(CartItem.cart_id == cart.id, CartItem.dish_id == dish_id))
    item = result.scalars().first()
    if item:
        item.quantity += quantity
    else:
        item = CartItem(cart_id=cart.id, dish_id=dish_id, quantity=quantity, price=dish.price)
        db.add(item)
    await db.commit()
    logger.info(f"User {user.id} added dish {dish_id} to cart {cart.id}")
    result = await db.execute(select(Cart).options(selectinload(Cart.items)).where(Cart.id == cart.id))
    cart = result.scalars().first()
    return cart

@router.get("/", response_model=CartResponse)
async def get_my_cart(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(select(Cart).options(selectinload(Cart.items)).where(Cart.user_id == user.id))
    cart = result.scalars().first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart is empty")
    return cart

@router.delete("/item/{item_id}", response_model=CartResponse)
async def remove_cart_item(item_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(select(CartItem).join(Cart).where(CartItem.id == item_id, Cart.user_id == user.id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    await db.delete(item)
    await db.commit()
    logger.info(f"User {user.id} removed item {item.id} from cart {item.cart_id}")
    result = await db.execute(select(Cart).options(selectinload(Cart.items)).where(Cart.id == item.cart_id))
    cart = result.scalars().first()
    return cart

@router.delete("/clear")
async def clear_cart(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(select(Cart).options(selectinload(Cart.items)).where(Cart.user_id == user.id))
    cart = result.scalars().first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    for item in cart.items:
        await db.delete(item)
    await db.commit()
    logger.info(f"User {user.id} cleared cart {cart.id}")
    return {"message": "Cart cleared successfully"}

@router.post("/checkout", response_model=OrderRead)
async def checkout(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    order = await order_crud.checkout_cart(db, current_user.id)
    logger.info(f"User {current_user.id} checked out and created order {order.id} with {len(order.items)} items")
    return order

@router.patch("/item/{item_id}/increase", response_model=CartResponse)
async def increase_item_quantity(item_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(select(CartItem).join(Cart).where(CartItem.id == item_id, Cart.user_id == user.id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.quantity += 1
    await db.commit()
    logger.info(f"User {user.id} increased quantity of item {item.id} in cart {item.cart_id} to {item.quantity}")
    result = await db.execute(select(Cart).options(selectinload(Cart.items)).where(Cart.id == item.cart_id))
    cart = result.scalars().first()
    return cart

@router.patch("/item/{item_id}/decrease", response_model=CartResponse)
async def decrease_item_quantity(item_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(select(CartItem).join(Cart).where(CartItem.id == item_id, Cart.user_id == user.id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.quantity > 1:
        item.quantity -= 1
        await db.commit()
        logger.info(f"User {user.id} decreased quantity of item {item.id} in cart {item.cart_id} to {item.quantity}")
    result = await db.execute(select(Cart).options(selectinload(Cart.items)).where(Cart.id == item.cart_id))
    cart = result.scalars().first()
    return cart
