from pydantic import BaseModel, Field
from typing import Optional

class RestaurantRead(BaseModel):
    id: int
    name: str
    address: str
    contact_info: str | None = None
    opening_hours: str | None = None

    class Config:
        orm_mode = True

class RestaurantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    address: str = Field(..., min_length=1, max_length=255)
    contact_info: Optional[str] = None
    opening_hours: Optional[str] = None

    
class RestaurantUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    contact_info: str | None = None
    opening_hours: str | None = None
