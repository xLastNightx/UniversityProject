# Бронирование встреч (время работы: с 9 до 17)

# Стурктура проекта:

<pre><code>
UniversityProject/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
├── REAADME.md
├── users.json
├── database.db
└── calendar/
    ├── backend/
    │   ├── app/
    │   |    ├── __init__.py
    │   |    ├── main.py
    │   |    ├── models.py
    │   |    ├── schemas.py
    │   |    ├── database.py
    │   |    ├── auth_utils.py
    │   |    ├── crud.py
    │   |    ├── email_utils.py
    │   |    └── routers/
    │   |        ├── bookings.py 
    |   |        ├── __init__.py
    │   |        └── auth.py  
    |   └── tests/
    │       ├── __init__.py
    │       └── test_auth.py
    └── frontend/
        ├── static/
        │   ├── css/
        │   │   └── style.css
        │   └── js/
        │       └── main.js
        └── templates/
            ├── base.html
            ├── login.html
            ├── register.html
            ├── bookings.html
            ├── change_password.html
            ├── reset_password.html
            └── create_booking.html
</code></pre>

Чтобы запустить проект, надо: 
### 1. Ввести в консоли docker-compose up --build
### 2. Перейти на сайт http://localhost:8000/
### 3. После завершения всех бронирований не забыть закрыть сессию командой docker-compose down
(чтобы прервать работу докера нажмите CTRL+C)
