import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Абсолютный путь к базе данных в контейнере
DB_PATH = "/app/database.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

print(f"DEBUG: Database path: {DB_PATH}")
print(f"DEBUG: Database exists: {os.path.exists(DB_PATH)}")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=True  # Включаем логирование SQL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()