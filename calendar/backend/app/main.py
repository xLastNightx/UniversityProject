from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .routers import bookings, auth
from .database import Base, engine
from fastapi import Request

# Создаём таблицы (только если их нет)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Booking Calendar API")

# Монтируем статику — путь внутри контейнера
app.mount("/static", StaticFiles(directory="/app/frontend/static"), name="static")

# Шаблоны
templates = Jinja2Templates(directory="/app/frontend/templates")

# Подключаем роутеры
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
from fastapi import Request

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})