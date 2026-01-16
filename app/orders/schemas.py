from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from app.restaurants.schemas import RestaurantBasic

class OrderItemCreate(BaseModel):
    dish_id: int
    quantity: int

class OrderItemRead(BaseModel):
    id: int
    dish_id: int
    quantity: int
    price: float

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    restaurant_id: int
    items: List[OrderItemCreate]
class OrderRead(BaseModel):
    id: int
    user_id: int
    total_price: float
    status: str
    created_at: datetime
    updated_at: datetime
    restaurant: RestaurantBasic
    items: List[OrderItemRead]

    class Config:
        from_attributes = True

class OrderUpdate(BaseModel):
    status: Optional[str] = None
