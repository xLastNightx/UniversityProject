from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    google_sub: Optional[str] = None


class UserOut(BaseModel):
    email: str
    name: str

    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    date: str  # "YYYY-MM-DD"
    time_slot: str  #" 09:00"


class BookingOut(BaseModel):
    id: int
    user_email: str
    date: str
    time_slot: str
    confirmed: bool

    class Config:
        from_attributes = True
