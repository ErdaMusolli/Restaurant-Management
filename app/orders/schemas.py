from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class OrderCreate(BaseModel):
    user_id: int
    restaurant_id: int
    total_price: float
    status: Optional[str] = "Pending"

class OrderRead(BaseModel):
    id: int
    user_id: int
    restaurant_id: int
    total_price: float
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    total_price: Optional[float] = None
