from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.utils.database import Base

class Dish(Base):
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    menu_id = Column(Integer, ForeignKey("menus.id"))

    menu = relationship("Menu", back_populates="dishes")
