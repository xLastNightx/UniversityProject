# calendar/backend/app/schemas.py

from pydantic import BaseModel
from typing import List, Optional

class BookingCreate(BaseModel):
    """
    Схема для создания бронирования (входные данные от формы)
    """
    date: str  # формат: "YYYY-MM-DD"
    time_slot: str  # например: "09:00"

class BookingOut(BaseModel):
    """
    Схема для вывода бронирования (возвращается в API или шаблоне)
    """
    id: int
    user_email: str
    date: str
    time_slot: str
    confirmed: bool

    class Config:
        from_attributes = True  # для совместимости с SQLAlchemy (вместо orm_mode)