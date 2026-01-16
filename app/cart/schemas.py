from pydantic import BaseModel, Field
from typing import Optional
class CartItemResponse(BaseModel):
    id: int
    dish_id: int
    quantity: int
    price: float

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    id: int
    restaurant_id: int
    items: list[CartItemResponse]

    class Config:
        from_attributes = True
