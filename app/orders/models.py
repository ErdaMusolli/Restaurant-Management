from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)

    total_price = Column(Float, nullable=False, default=0.0)
    status = Column(String, default="Pending")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")
    restaurant = relationship("Restaurant")
    items = relationship(
    "OrderItem",
    back_populates="order",
    cascade="all, delete",
    lazy="selectin"
)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    dish_id = Column(Integer, ForeignKey("dishes.id"), nullable=False)

    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)  

    order = relationship("Order", back_populates="items")
    dish = relationship("Dish")