from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.utils.database import Base

class Menu(Base):
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))

    restaurant = relationship("Restaurant", back_populates="menus")
    dishes = relationship("Dish", back_populates="menu")


