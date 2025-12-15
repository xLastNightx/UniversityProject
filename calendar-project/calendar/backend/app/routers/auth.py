from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from .. import auth, crud, schemas
from ..database import SessionLocal

router = APIRouter()

@router.get("/login")
async def login_google():
    return RedirectResponse(
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={auth.GOOGLE_CLIENT_ID}&"
        f"redirect_uri=http://localhost:8000/auth/callback&"
        f"scope=openid email profile&"
        f"response_type=code"
    )

@router.get("/auth/callback")
async def auth_callback(code: str, db: Session = Depends(auth.get_db)):
    raise HTTPException(status_code=501, detail="OAuth через code требует бэкенд-обмена. Для упрощения используйте id_token с фронта.")

@router.post("/auth/verify")
async def verify_token(token: dict, db: Session = Depends(auth.get_db)):
    id_info = auth.verify_google_token(token["credential"])
    email = id_info["email"]
    name = id_info.get("name", "Unknown")
    google_sub = id_info["sub"]

    user = crud.get_user_by_email(db, email)
    if not user:
        user = crud.create_user(db, schemas.UserCreate(email=email, name=name, google_sub=google_sub))
    return {"email": user.email, "name": user.name}