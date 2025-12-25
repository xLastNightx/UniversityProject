# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .routers import bookings, auth
from .database import Base, engine
import os

# Проверяем и создаем базу данных
print("Инициализация базы данных...")
db_path = "/app/database.db"

if not os.path.exists(db_path):
    print(f"Создаю файл базы данных: {db_path}")
    # Создаем пустой файл
    with open(db_path, 'w') as f:
        pass
    os.chmod(db_path, 0o666)  # Даем права на чтение/запись

try:
    # Создаём таблицы
    Base.metadata.create_all(bind=engine)
    print("Таблицы созданы успешно")
except Exception as e:
    print(f"Ошибка создания таблиц: {e}")
    # Пробуем альтернативный путь
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.close()
    Base.metadata.create_all(bind=engine)

app = FastAPI(title="Booking Calendar API")

# Монтируем статику
app.mount("/static", StaticFiles(directory="/app/frontend/static"), name="static")

# Шаблоны
templates = Jinja2Templates(directory="/app/frontend/templates")

# Подключаем роутеры
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(bookings.router, prefix="/bookings", tags=["bookings"])

@app.get("/")
async def root():
    return {"message": "Booking System API"}