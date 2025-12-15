from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .routers import bookings, auth
from .database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="calendar/frontend/static"), name="static")

app.include_router(auth.router, prefix="/auth")
app.include_router(bookings.router, prefix="/bookings")
