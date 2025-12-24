from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    """РЎС…РµРјР° РґР»СЏ СЃРѕР·РґР°РЅРёСЏ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ"""
    email: EmailStr
    name: str
    password: str
    google_sub: Optional[str] = None


class UserOut(BaseModel):
    """РЎС…РµРјР° РґР»СЏ РІС‹РІРѕРґР° РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ"""
    email: str
    name: str

    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    """
    РЎС…РµРјР° РґР»СЏ СЃРѕР·РґР°РЅРёСЏ Р±СЂРѕРЅРёСЂРѕРІР°РЅРёСЏ (РІС…РѕРґРЅС‹Рµ РґР°РЅРЅС‹Рµ РѕС‚ С„РѕСЂРјС‹)
    """
    date: str  # С„РѕСЂРјР°С‚: "YYYY-MM-DD"
    time_slot: str  # РЅР°РїСЂРёРјРµСЂ: "09:00"


class BookingOut(BaseModel):
    """
    РЎС…РµРјР° РґР»СЏ РІС‹РІРѕРґР° Р±СЂРѕРЅРёСЂРѕРІР°РЅРёСЏ (РІРѕР·РІСЂР°С‰Р°РµС‚СЃСЏ РІ API РёР»Рё С€Р°Р±Р»РѕРЅРµ)
    """
    id: int
    user_email: str
    date: str
    time_slot: str
    confirmed: bool

    class Config:
        from_attributes = True
