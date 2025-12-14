from sqlalchemy import Column, Integer, String, DateTime, Boolean
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    google_sub = Column(String, unique=True, index=True)
    name = Column(String)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True)
    date = Column(String)  # "YYYY-MM-DD"
    time_slot = Column(String)  # "09:00", "11:00", etc.
    confirmed = Column(Boolean, default=False)