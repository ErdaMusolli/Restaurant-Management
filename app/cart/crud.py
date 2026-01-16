from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import Cart, CartItem, Dish
from .cache import get_cart_cache, set_cart_cache, delete_cart_cache

async def get_cart_by_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(Cart).where(Cart.user_id == user_id))
    return result.scalars().first()

async def add_item_to_cart(db: AsyncSession, user_id: int, dish_id: int, quantity: int = 1):
    cart = await get_cart_by_user(db, user_id)
    if not cart:
        cart = Cart(user_id=user_id, restaurant_id=1)  
        db.add(cart)
        await db.commit()
        await db.refresh(cart)

    result = await db.execute(select(Dish).where(Dish.id == dish_id))
    dish = result.scalars().first()
    if not dish:
        return None

   
    cart_item = next((i for i in cart.items if i.dish_id == dish_id), None)
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(cart_id=cart.id, dish_id=dish.id, quantity=quantity, price=dish.price)
        db.add(cart_item)

    await db.commit()
    await db.refresh(cart)
    return cart

async def remove_item_from_cart(db: AsyncSession, cart_item_id: int):
    result = await db.execute(select(CartItem).where(CartItem.id == cart_item_id))
    item = result.scalars().first()
    if item:
        await db.delete(item)
        await db.commit()
    return item
    
async def get_cart(db, user_id: int):
    cached = await get_cart_cache(user_id)
    if cached:
        return cached

    result = await db.execute(select(Cart).where(Cart.user_id == user_id).options(selectinload(Cart.items))))
    cart = result.scalars().first()
    if cart:
        await set_cart_cache(user_id, cart_to_dict(cart))
    return cart