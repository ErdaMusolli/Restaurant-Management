from pydantic import BaseModel
from typing import Optional

class MenuBase(BaseModel):
    name: str
    description: Optional[str] = None
    restaurant_id: Optional[int] = None

class MenuCreate(MenuBase):
    pass

class MenuUpdate(MenuBase):
    pass

class MenuOut(MenuBase):
    id: int

    class Config:
        orm_mode = True


