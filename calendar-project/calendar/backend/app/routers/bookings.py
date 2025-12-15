from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from .. import auth, crud, schemas, email_utils
from ..database import SessionLocal
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="calendar/frontend/templates")

VALID_SLOTS = ["09:00", "11:00", "13:00", "15:00"]

@router.get("/", response_class=HTMLResponse)
async def bookings_page(request: Request, db: Session = Depends(auth.get_db)):
    # Здесь предполагается, что email в сессии или куках
    # Для упрощения — передаём через URL (в реальном — через сессию)
    email = request.query_params.get("email")
    if not email:
        return RedirectResponse("/login")
    bookings = crud.get_bookings_by_user(db, email)
    return templates.TemplateResponse("bookings.html", {"request": request, "bookings": bookings, "email": email})

@router.get("/create", response_class=HTMLResponse)
async def create_booking_form(request: Request):
    email = request.query_params.get("email")
    if not email:
        return RedirectResponse("/login")
    return templates.TemplateResponse("create_booking.html", {"request": request, "email": email})

@router.post("/create")
async def create_booking(
    request: Request,
    booking: schemas.BookingCreate,
    db: Session = Depends(auth.get_db)
):
    email = request.query_params.get("email")
    if not email:
        raise HTTPException(status_code=401)

    # Проверка формата даты
    try:
        datetime.strptime(booking.date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат даты (YYYY-MM-DD)")

    # Проверка слота
    if booking.time_slot not in VALID_SLOTS:
        raise HTTPException(status_code=400, detail="Недопустимое время. Доступно: 09:00, 11:00, 13:00, 15:00")

    # Проверка переполнения (макс 4 брони в день — по слотам)
    existing = crud.get_all_bookings_on_date(db, booking.date)
    if any(b.time_slot == booking.time_slot for b in existing):
        raise HTTPException(status_code=400, detail="Этот слот уже занят!")

    new_booking = crud.create_booking(db, booking, email)

    # Отправка email
    body = f"""
    <h3>Ваша встреча подтверждена!</h3>
    <p>Дата: {booking.date}</p>
    <p>Время: {booking.time_slot}</p>
    <p><strong>Пожалуйста, приходите заранее и не опаздывайте!</strong></p>
    """
    await email_utils.send_email(email, "Встреча забронирована", body)

    return RedirectResponse(f"/?email={email}", status_code=303)

@router.get("/delete/{booking_id}")
async def delete_booking_route(booking_id: int, request: Request, db: Session = Depends(auth.get_db)):
    email = request.query_params.get("email")
    if not email:
        raise HTTPException(status_code=401)
    success = crud.delete_booking(db, booking_id)
    if not success:
        raise HTTPException(status_code=404)
    return RedirectResponse(f"/?email={email}", status_code=303)

@router.get("/search")
async def search_bookings(
    q: str = Query(None),
    email: str = Query(...),
    db: Session = Depends(auth.get_db)
):
    all_bookings = crud.get_bookings_by_user(db, email)
    if q:
        filtered = [b for b in all_bookings if q in b.date or q in b.time_slot]
    else:
        filtered = all_bookings
    return {"results": filtered}
