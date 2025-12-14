from fastapi import Depends, HTTPException
from google.auth.transport import requests
from google.oauth2 import id_token
from .database import SessionLocal

GOOGLE_CLIENT_ID = "ваш-google-client-id.apps.googleusercontent.com"


def verify_google_token(token: str):
    try:
        id_info = id_token.verify_oauth2_token(
            token, requests.Request(), GOOGLE_CLIENT_ID)
        if id_info["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            raise ValueError("Неверный издатель")
        return id_info
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный токен")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
