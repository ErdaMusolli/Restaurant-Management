from pydantic import BaseModel
from typing import Optional

class DishBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    menu_id: int

class DishCreate(DishBase):
    pass

class DishUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

class DishOut(DishBase):
    id: int

    class Config:
        orm_mode = True
