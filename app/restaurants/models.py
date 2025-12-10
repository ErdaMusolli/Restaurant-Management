from sqlalchemy import Column, Integer, String
from app.database import Base

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    address = Column(String(255), nullable=False)
    contact_info = Column(String(100), nullable=True)
    opening_hours = Column(String(100), nullable=True)