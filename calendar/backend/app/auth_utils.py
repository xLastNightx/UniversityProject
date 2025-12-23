import json
import hashlib
import os
import secrets
from typing import Dict, Optional

USERS_FILE = "/app/users.json"  # Абсолютный путь в контейнере
def load_users() -> Dict:
    """Загрузить пользователей из файла"""
    if not os.path.exists(USERS_FILE):
        print(f"Users file not found at {USERS_FILE}")
        return {}
    
    try:
        # Пробуем разные кодировки
        for encoding in ['utf-8-sig', 'utf-8', 'cp1251']:
            try:
                with open(USERS_FILE, "r", encoding=encoding) as f:
                    content = f.read().strip()
                    if not content:
                        return {}
                    return json.loads(content)
            except UnicodeDecodeError:
                continue
            except json.JSONDecodeError as e:
                print(f"JSON decode error with encoding {encoding}: {e}")
                # Если JSON поврежден, создаем новый
                break
        
        # Если все кодировки не сработали или JSON поврежден
        print(f"Creating new users file at {USERS_FILE}")
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}
        
    except Exception as e:
        print(f"Unexpected error loading users: {e}")
        return {}
    
    
def save_users(users: Dict):
    """Сохранить пользователей в файл"""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def hash_password(password: str) -> str:
    """Хеширование пароля"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Проверка пароля"""
    return hash_password(password) == hashed

def register_user(email: str, password: str, name: str) -> bool:
    """Регистрация нового пользователя"""
    users = load_users()
    if email in users:
        return False  # Пользователь уже существует
    
    users[email] = {
        "email": email,
        "password_hash": hash_password(password),
        "name": name,
        "reset_code": None,
        "reset_code_expiry": None
    }
    save_users(users)
    return True

def authenticate_user(email: str, password: str) -> bool:
    """Аутентификация пользователя"""
    users = load_users()
    if email not in users:
        return False
    return verify_password(password, users[email]["password_hash"])

def get_user(email: str) -> Optional[Dict]:
    """Получить данные пользователя"""
    users = load_users()
    return users.get(email)

def change_password(email: str, old_password: str, new_password: str) -> bool:
    """Смена пароля"""
    users = load_users()
    if email not in users:
        return False
    if not verify_password(old_password, users[email]["password_hash"]):
        return False
    
    users[email]["password_hash"] = hash_password(new_password)
    save_users(users)
    return True

def generate_reset_code(email: str) -> Optional[str]:
    """Генерация кода для сброса пароля"""
    users = load_users()
    if email not in users:
        return None
    
    reset_code = secrets.token_urlsafe(8)
    users[email]["reset_code"] = reset_code
    # Код действует 1 час
    import time
    users[email]["reset_code_expiry"] = time.time() + 3600
    save_users(users)
    return reset_code

def reset_password_with_code(email: str, code: str, new_password: str) -> bool:
    """Сброс пароля с кодом"""
    users = load_users()
    if email not in users:
        return False
    
    user_data = users[email]
    import time
    current_time = time.time()
    
    if (user_data["reset_code"] == code and 
        user_data["reset_code_expiry"] and 
        current_time < user_data["reset_code_expiry"]):
        
        users[email]["password_hash"] = hash_password(new_password)
        users[email]["reset_code"] = None
        users[email]["reset_code_expiry"] = None
        save_users(users)
        return True
    return False