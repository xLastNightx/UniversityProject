from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from .. import auth_utils, email_utils
from ..database import SessionLocal
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="/app/frontend/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    if auth_utils.authenticate_user(email, password):
        response = RedirectResponse(f"/bookings/?email={email}", status_code=303)
        response.set_cookie(key="email", value=email)
        return response
    return templates.TemplateResponse(
        "login.html", 
        {"request": request, "error": "Неверный email или пароль"}
    )

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    name: str = Form(...)
):
    if password != confirm_password:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Пароли не совпадают"}
        )
    
    if auth_utils.register_user(email, password, name):
        response = RedirectResponse(f"/bookings/?email={email}", status_code=303)
        response.set_cookie(key="email", value=email)
        return response
    
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "error": "Пользователь с таким email уже существует"}
    )

@router.get("/change-password", response_class=HTMLResponse)
async def change_password_page(request: Request):
    return templates.TemplateResponse("change_password.html", {"request": request})

@router.post("/change-password")
async def change_password_route(
    request: Request,
    email: str = Form(...),
    old_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    if new_password != confirm_password:
        return templates.TemplateResponse(
            "change_password.html",
            {"request": request, "error": "Новые пароли не совпадают"}
        )
    
    if auth_utils.change_password(email, old_password, new_password):
        return templates.TemplateResponse(
            "change_password.html",
            {"request": request, "success": "Пароль успешно изменен"}
        )
    
    return templates.TemplateResponse(
        "change_password.html",
        {"request": request, "error": "Неверный email или старый пароль"}
    )

@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request):
    return templates.TemplateResponse("reset_password.html", {"request": request})

@router.post("/reset-password")
async def reset_password_request(
    request: Request,
    email: str = Form(...)
):
    user = auth_utils.get_user(email)
    if not user:
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "error": "Пользователь не найден"}
        )
    
    reset_code = auth_utils.generate_reset_code(email)
    if reset_code:
        # Выводим код в консоль для тестирования
        print(f"\n{'='*60}")
        print(f"RESET PASSWORD CODE FOR: {email}")
        print(f"CODE: {reset_code}")
        print(f"{'='*60}\n")
        
        # Отправка email с кодом (в тестовом режиме только вывод в консоль)
        body = f"""
        <h3>Сброс пароля</h3>
        <p>Для сброса пароля используйте код: <strong>{reset_code}</strong></p>
        <p>Код действителен в течение 1 часа.</p>
        """
        
        try:
            await email_utils.send_email(email, "Сброс пароля", body)
            success_message = "Код для сброса пароля сгенерирован. Проверьте консоль сервера."
        except Exception as e:
            print(f"Email sending simulation failed: {e}")
            success_message = f"Код для сброса пароля: {reset_code} (проверьте консоль)"
        
        return templates.TemplateResponse(
            "reset_password.html",
            {
                "request": request, 
                "success": success_message,
                "show_reset_form": True,
                "email": email
            }
        )
    
    return templates.TemplateResponse(
        "reset_password.html",
        {"request": request, "error": "Ошибка генерации кода"}
    )

@router.post("/reset-password-confirm")
async def reset_password_confirm(
    request: Request,
    email: str = Form(...),
    code: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    if new_password != confirm_password:
        return templates.TemplateResponse(
            "reset_password.html",
            {
                "request": request,
                "error": "Пароли не совпадают",
                "show_reset_form": True,
                "email": email
            }
        )
    
    if auth_utils.reset_password_with_code(email, code, new_password):
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "success": "Пароль успешно сброшен"}
        )
    
    return templates.TemplateResponse(
        "reset_password.html",
        {
            "request": request,
            "error": "Неверный или просроченный код",
            "show_reset_form": True,
            "email": email
        }
    )

@router.get("/logout")
async def logout():
    response = RedirectResponse("/auth/login")
    response.delete_cookie(key="email")
    return response