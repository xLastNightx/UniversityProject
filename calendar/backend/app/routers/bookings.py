from fastapi import APIRouter, Depends, HTTPException, Request, Query, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime, timedelta
import calendar as cal_lib
from typing import List, Dict
from .. import auth_utils, crud, schemas, email_utils, models
from ..database import SessionLocal
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="/app/frontend/templates")

VALID_SLOTS = ["09:00", "11:00", "13:00", "15:00"]

def add_hours(time_str: str, hours: int) -> str:
    """Добавляет часы к времени"""
    hour = int(time_str.split(":")[0])
    new_hour = hour + hours
    return f"{new_hour:02d}:00"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def add_hours(time_str: str, hours: int) -> str:
    """Добавляет часы к времени"""
    hour = int(time_str.split(":")[0])
    new_hour = hour + hours
    return f"{new_hour:02d}:00"

def get_available_slots(db: Session, date: str, exclude_booking_id: int = None) -> List[Dict]:
    """Возвращает доступные слоты на дату"""
    existing = crud.get_all_bookings_on_date(db, date)
    booked = [b.time_slot for b in existing if b.id != exclude_booking_id]
    
    slots = []
    for slot in VALID_SLOTS:
        slots.append({
            "slot": slot,
            "available": slot not in booked,
            "end_time": add_hours(slot, 2)
        })
    return slots

@router.get("/", response_class=HTMLResponse)
async def bookings_page(
    request: Request,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    q: str = Query(None)
):
    email = request.cookies.get("email")
    if not email:
        return RedirectResponse("/auth/login")
    
    if not auth_utils.get_user(email):
        return RedirectResponse("/auth/login")
    
    # Пагинация
    skip = (page - 1) * limit
    
    # Поиск
    bookings_query = db.query(models.Booking).filter(
        models.Booking.user_email == email
    )
    
    if q:
        bookings_query = bookings_query.filter(
            or_(
                models.Booking.date.contains(q),
                models.Booking.time_slot.contains(q)
            )
        )
    
    # Получаем общее количество
    total_bookings = bookings_query.count()
    
    # Получаем данные для страницы
    bookings = bookings_query.order_by(models.Booking.date.desc()).offset(skip).limit(limit).all()
    
    # Добавляем время окончания
    for booking in bookings:
        booking.end_time = add_hours(booking.time_slot, 2)
    
    # Предстоящие записи (ближайшие 3)
    upcoming = db.query(models.Booking).filter(
        models.Booking.user_email == email,
        models.Booking.date >= datetime.now().strftime("%Y-%m-%d")
    ).order_by(models.Booking.date).limit(3).all()
    
    # Добавляем дни до записи
    for booking in upcoming:
        booking_date = datetime.strptime(booking.date, "%Y-%m-%d")
        booking.days_until = (booking_date - datetime.now()).days
        booking.end_time = add_hours(booking.time_slot, 2)
    
    # Расчеты для пагинации
    total_pages = (total_bookings + limit - 1) // limit
    start_index = skip + 1 if total_bookings > 0 else 0
    end_index = min(skip + limit, total_bookings)
    
    return templates.TemplateResponse(
        "bookings.html",
        {
            "request": request,
            "bookings": bookings,
            "upcoming_bookings": upcoming,
            "email": email,
            "page": page,
            "total_pages": total_pages,
            "limit": limit,
            "search_query": q,
            "total_bookings": total_bookings,
            "start_index": start_index,
            "end_index": end_index
        }
    )

@router.get("/create", response_class=HTMLResponse)
async def create_booking_page(
    request: Request,
    date: str = Query(None),
    db: Session = Depends(get_db)
):
    email = request.cookies.get("email")
    if not email:
        return RedirectResponse("/auth/login")
    
    if not auth_utils.get_user(email):
        return RedirectResponse("/auth/login")
    
    # Функция для добавления часов
    def add_hours_local(time_str: str, hours: int) -> str:
        hour = int(time_str.split(":")[0])
        new_hour = hour + hours
        return f"{new_hour:02d}:00"
    
    # Текущая дата
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    # ДЕБАГ: выводим переданную дату
    print(f"DEBUG: Переданная дата: {date}")
    
    # Используем переданную дату или сегодняшнюю
    selected_date = date if date else today_date
    
    # Валидируем дату
    try:
        datetime.strptime(selected_date, "%Y-%m-%d")
    except ValueError:
        print(f"DEBUG: Неверная дата '{selected_date}', используем сегодня")
        selected_date = today_date
    
    print(f"DEBUG: Используемая дата: {selected_date}")
    
    # Получаем занятые слоты на выбранную дату
    existing_bookings = crud.get_all_bookings_on_date(db, selected_date)
    
    # Генерируем слоты
    booked_slots = [b.time_slot for b in existing_bookings]
    time_slots = []
    for slot in VALID_SLOTS:
        disabled = slot in booked_slots
        end_time = add_hours_local(slot, 2)
        time_slots.append({
            "value": slot,
            "label": f"{slot}–{end_time}",
            "disabled": disabled
        })
    
    return templates.TemplateResponse(
        "create_booking.html",
        {
            "request": request,
            "email": email,
            "selected_date": selected_date,  # Важно: передаем выбранную дату
            "today": today_date,
            "time_slots": time_slots,
        }
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
        return templates.TemplateResponse(
            "create_booking.html",
            {
                "request": request,
                "email": email,
                "selected_date": date,
                "today": datetime.now().strftime("%Y-%m-%d"),
                "error": "Неверный слот времени"
            }
        )
    
    # Валидация даты
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return templates.TemplateResponse(
            "create_booking.html",
            {
                "request": request,
                "email": email,
                "selected_date": date,
                "today": datetime.now().strftime("%Y-%m-%d"),
                "error": "Неверный формат даты"
            }
        )
    
    # Проверка, свободен ли слот НА ЭТУ ДАТУ
    existing_bookings = crud.get_all_bookings_on_date(db, date)
    for booking in existing_bookings:
        if booking.time_slot == time_slot:
            # Перегенерируем слоты для отображения
            booked_slots = [b.time_slot for b in existing_bookings]
            time_slots = []
            for slot in VALID_SLOTS:
                disabled = slot in booked_slots
                end_time = add_hours(slot, 2)
                time_slots.append({
                    "value": slot,
                    "label": f"{slot}–{end_time}",
                    "disabled": disabled
                })
            
            return templates.TemplateResponse(
                "create_booking.html",
                {
                    "request": request,
                    "email": email,
                    "selected_date": date,
                    "today": datetime.now().strftime("%Y-%m-%d"),
                    "time_slots": time_slots,
                    "booked_slots": existing_bookings,
                    "error": f"Время {time_slot} на {date} уже занято"
                }
            )
    
    # Создание бронирования
    booking_data = schemas.BookingCreate(date=date, time_slot=time_slot)
    crud.create_booking(db, booking_data, email)
    
    return RedirectResponse(f"/bookings/?email={email}", status_code=303)

@router.get("/edit/{booking_id}", response_class=HTMLResponse)
async def edit_booking_page(
    request: Request,
    booking_id: int,
    db: Session = Depends(get_db)
):
    email = request.cookies.get("email")
    if not email:
        return RedirectResponse("/auth/login")
    
    if not auth_utils.get_user(email):
        return RedirectResponse("/auth/login")
    
    booking = crud.get_booking_by_id(db, booking_id)
    if not booking or booking.user_email != email:
        return RedirectResponse("/bookings/")
    
    # Получаем занятые слоты на эту дату
    existing_bookings = crud.get_all_bookings_on_date(db, booking.date)
    booked_slots = [b.time_slot for b in existing_bookings if b.id != booking_id]
    
    # Генерируем список слотов
    time_slots = []
    for slot in VALID_SLOTS:
        disabled = slot in booked_slots
        end_time = add_hours(slot, 2)
        time_slots.append({
            "value": slot,
            "label": f"{slot}–{end_time}",
            "disabled": disabled
        })
    
    # Минимальная дата (сегодня)
    min_date = datetime.now().strftime("%Y-%m-%d")
    
    return templates.TemplateResponse(
        "edit_booking.html",
        {
            "request": request,
            "booking": booking,
            "email": email,
            "time_slots": time_slots,
            "min_date": min_date
        }
    )

@router.post("/edit/{booking_id}")
async def edit_booking(
    request: Request,
    booking_id: int,
    date: str = Form(...),
    time_slot: str = Form(...),
    db: Session = Depends(get_db)
):
    email = request.cookies.get("email")
    if not email:
        return RedirectResponse("/auth/login")
    
    # Проверяем принадлежность бронирования
    booking = crud.get_booking_by_id(db, booking_id)
    if not booking or booking.user_email != email:
        return RedirectResponse("/bookings/")
    
    # Проверяем доступность нового слота
    existing_bookings = crud.get_all_bookings_on_date(db, date)
    for existing in existing_bookings:
        if existing.time_slot == time_slot and existing.id != booking_id:
            # Получаем занятые слоты для отображения
            booked_slots = [b.time_slot for b in existing_bookings if b.id != booking_id]
            time_slots = []
            for slot in VALID_SLOTS:
                disabled = slot in booked_slots
                end_time = add_hours(slot, 2)
                time_slots.append({
                    "value": slot,
                    "label": f"{slot}–{end_time}",
                    "disabled": disabled
                })
            
            return templates.TemplateResponse(
                "edit_booking.html",
                {
                    "request": request,
                    "booking": booking,
                    "email": email,
                    "error": "Это время уже занято",
                    "time_slots": time_slots,
                    "min_date": datetime.now().strftime("%Y-%m-%d")
                }
            )
    
    # Обновляем бронирование
    booking.date = date
    booking.time_slot = time_slot
    db.commit()
    
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
    
    # Добавляем время окончания
    for booking in filtered:
        booking.end_time = add_hours(booking.time_slot, 2)
    
    return templates.TemplateResponse(
        "bookings.html",
        {
            "request": request,
            "bookings": filtered,
            "email": email,
            "search_query": q,
            "page": 1,
            "total_pages": 1,
            "limit": len(filtered),
            "total_bookings": len(filtered),
            "start_index": 1 if filtered else 0,
            "end_index": len(filtered)
        }
    )

@router.get("/calendar", response_class=HTMLResponse)
async def calendar_view(
    request: Request,
    year: int = Query(None),
    month: int = Query(None),
    db: Session = Depends(get_db)
):
    email = request.cookies.get("email")
    if not email:
        return RedirectResponse("/auth/login")
    
    # Текущая дата - СЕГОДНЯ
    today = datetime.now()
    print(f"DEBUG: Сегодня: {today}")
    
    if not year:
        year = today.year
    if not month:
        month = today.month  # ТЕКУЩИЙ МЕСЯЦ
    
    print(f"DEBUG: Показываем месяц: {year}-{month}")
    
    try:
        cal = cal_lib.monthcalendar(year, month)
    except Exception as e:
        print(f"DEBUG: Ошибка календаря: {e}")
        # Если ошибка, используем текущий месяц
        year = today.year
        month = today.month
        cal = cal_lib.monthcalendar(year, month)
    
    # Преобразуем календарь в структуру с данными
    month_calendar = []
    for week in cal:
        week_days = []
        for day in week:
            if day == 0:
                week_days.append({"day": None, "month": None, "bookings": []})
            else:
                day_date = f"{year}-{month:02d}-{day:02d}"
                
                # Получаем бронирования на этот день
                day_bookings = db.query(models.Booking).filter(
                    models.Booking.date == day_date
                ).all()
                
                week_days.append({
                    "day": day,
                    "month": month,
                    "is_today": (year == today.year and month == today.month and day == today.day),
                    "bookings": day_bookings
                })
        month_calendar.append(week_days)
    
    # Навигация по месяцам
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    # Русские названия месяцев
    month_names = [
        "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
        "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    ]
    
    return templates.TemplateResponse(
        "calendar.html",
        {
            "request": request,
            "email": email,
            "calendar": month_calendar,
            "year": year,
            "month": month,
            "current_month": month,
            "month_name": month_names[month - 1] if 1 <= month <= 12 else month_names[today.month - 1],
            "prev_year": prev_year,
            "prev_month": prev_month,
            "next_year": next_year,
            "next_month": next_month,
        }
    )

@router.get("/time-slots", response_class=HTMLResponse)
async def get_time_slots(
    request: Request,
    date: str = Query(...),
    db: Session = Depends(get_db)
):
    """Возвращает доступные временные слоты для выбранной даты (AJAX)"""
    if not date:
        return HTMLResponse("")
    
    try:
        # Проверяем дату
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return HTMLResponse("<p class='text-danger'>Неверная дата</p>")
    
    # Получаем занятые слоты ТОЛЬКО на эту дату
    existing_bookings = crud.get_all_bookings_on_date(db, date)
    booked_slots = [b.time_slot for b in existing_bookings]
    
    # Генерируем слоты
    time_slots = []
    for slot in VALID_SLOTS:
        disabled = slot in booked_slots
        end_time = add_hours(slot, 2)
        time_slots.append({
            "value": slot,
            "label": f"{slot}–{end_time}",
            "disabled": disabled
        })
    
    return templates.TemplateResponse(
        "time_slots_partial.html",
        {
            "time_slots": time_slots,
            "request": request
        }
    )

@router.get("/debug/calendar")
async def debug_calendar(
    request: Request,
    year: int = Query(None),
    month: int = Query(None),
    db: Session = Depends(get_db)
):
    """Endpoint для отладки календаря"""
    today = datetime.now()
    
    return {
        "today": today.strftime("%Y-%m-%d"),
        "requested_year": year,
        "requested_month": month,
        "actual_year": today.year if not year else year,
        "actual_month": today.month if not month else month,
        "url": str(request.url)
    }

@router.get("/debug/db")
async def debug_database(db: Session = Depends(get_db)):
    """Проверка состояния базы данных"""
    import os
    
    # Проверяем файл базы данных
    db_path = "/app/database.db"
    db_exists = os.path.exists(db_path)
    db_size = os.path.getsize(db_path) if db_exists else 0
    
    # Считаем записи
    total_bookings = db.query(models.Booking).count()
    all_bookings = db.query(models.Booking).all()
    
    return {
        "database_file": db_path,
        "database_exists": db_exists,
        "database_size": db_size,
        "total_bookings": total_bookings,
        "bookings": [
            {
                "id": b.id,
                "user_email": b.user_email,
                "date": b.date,
                "time_slot": b.time_slot,
                "confirmed": b.confirmed
            }
            for b in all_bookings[:10]  # Первые 10 записей
        ]
    }

@router.get("/debug/date")
async def debug_date():
    from datetime import datetime
    return {
        "current_date": datetime.now().strftime("%Y-%m-%d"),
        "current_year": datetime.now().year,
        "current_month": datetime.now().month,
        "current_day": datetime.now().day,
        "timestamp": datetime.now().isoformat()
    }