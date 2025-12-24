# bookings.py - добавьте после существующего кода
from fastapi import APIRouter, Depends, HTTPException, Request, Query, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime
from .. import auth_utils, crud, schemas, email_utils
from ..database import SessionLocal
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="/app/frontend/templates")

VALID_SLOTS = ["09:00", "11:00", "13:00", "15:00"]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
async def bookings_page(
    request: Request,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50)
):
    email = request.cookies.get("email")
    if not email:
        return RedirectResponse("/auth/login")
    
    if not auth_utils.get_user(email):
        return RedirectResponse("/auth/login")
    
    skip = (page - 1) * limit
    bookings = crud.get_bookings_by_user(db, email, skip=skip, limit=limit)
    total_bookings = len(crud.get_bookings_by_user(db, email, skip=0, limit=1000))
    total_pages = (total_bookings + limit - 1) // limit
    
    return templates.TemplateResponse(
        "bookings.html",
        {
            "request": request,
            "bookings": bookings,
            "email": email,
            "page": page,
            "total_pages": total_pages,
            "limit": limit
        }
    )

# ДОБАВЬТЕ ЭТИ НОВЫЕ ENDPOINT'ы:

@router.get("/create", response_class=HTMLResponse)
async def create_booking_page(request: Request):
    email = request.cookies.get("email")
    if not email:
        return RedirectResponse("/auth/login")
    
    if not auth_utils.get_user(email):
        return RedirectResponse("/auth/login")
    
    return templates.TemplateResponse(
        "create_booking.html",
        {"request": request, "email": email}
    )

@router.post("/create")
async def create_booking(
    request: Request,
    date: str = Form(...),
    time_slot: str = Form(...),
    db: Session = Depends(get_db)
):
    email = request.cookies.get("email")
    if not email:
        return RedirectResponse("/auth/login")
    
    if not auth_utils.get_user(email):
        return RedirectResponse("/auth/login")
    
    # Валидация слота времени
    if time_slot not in VALID_SLOTS:
        raise HTTPException(status_code=400, detail="Неверный слот времени")
    
    # Валидация даты
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат даты")
    
    # Проверка, свободен ли слот
    existing_bookings = crud.get_all_bookings_on_date(db, date)
    for booking in existing_bookings:
        if booking.time_slot == time_slot:
            return templates.TemplateResponse(
                "create_booking.html",
                {
                    "request": request,
                    "email": email,
                    "error": "Это время уже занято"
                }
            )
    
    # Создание бронирования
    booking_data = schemas.BookingCreate(date=date, time_slot=time_slot)
    crud.create_booking(db, booking_data, email)
    
    return RedirectResponse(f"/bookings/?email={email}", status_code=303)

@router.get("/delete/{booking_id}")
async def delete_booking(
    booking_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    email = request.cookies.get("email")
    if not email:
        return RedirectResponse("/auth/login")
    
    # Проверяем, что бронирование принадлежит пользователю
    booking = crud.get_booking_by_id(db, booking_id)
    if booking and booking.user_email == email:
        crud.delete_booking(db, booking_id)
    
    return RedirectResponse(f"/bookings/?email={email}", status_code=303)

@router.get("/search", response_class=HTMLResponse)
async def search_bookings(
    request: Request,
    q: str = Query(""),
    db: Session = Depends(get_db)
):
    email = request.cookies.get("email")
    if not email:
        return RedirectResponse("/auth/login")
    
    if not auth_utils.get_user(email):
        return RedirectResponse("/auth/login")
    
    # Простой поиск по дате или времени
    all_bookings = crud.get_bookings_by_user(db, email, skip=0, limit=1000)
    if q:
        filtered = [b for b in all_bookings if q in b.date or q in b.time_slot]
    else:
        filtered = all_bookings
    
    return templates.TemplateResponse(
        "bookings.html",
        {
            "request": request,
            "bookings": filtered,
            "email": email,
            "search_query": q,
            "page": 1,
            "total_pages": 1,
            "limit": len(filtered)
        }
    )