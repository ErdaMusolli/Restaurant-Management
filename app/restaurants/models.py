from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    address = Column(String(255), nullable=False)
    contact_info = Column(String(100), nullable=True)
    opening_hours = Column(String(100), nullable=True)

    menus = relationship(
        "Menu",
        back_populates="restaurant",
        cascade="all, delete-orphan"
    )