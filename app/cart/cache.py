from app.database import redis
import json

async def get_cart_cache(user_id: int):
    data = await redis.get(f"cart:{user_id}")
    if data:
        return json.loads(data)
    return None

async def set_cart_cache(user_id: int, cart_data, expire=300):
    await redis.set(f"cart:{user_id}", json.dumps(cart_data), ex=expire)

async def delete_cart_cache(user_id: int):
    await redis.delete(f"cart:{user_id}")
