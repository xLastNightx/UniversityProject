# Стурктура проекта:

<pre><code>
UniversityProject/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
├── REAADME.md
└── calendar/
    ├── backend/
    │   ├── app/
    │   |    ├── main.py
    │   |    ├── models.py
    │   |    ├── schemas.py
    │   |    ├── database.py
    │   |    ├── auth_utils.py
    │   |    ├── crud.py
    │   |    ├── email_utils.py
    │   |    └── routers/
    │   |        ├── bookings.py
    |   |        ├── __init.py__
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

Чтобы запустить проект, надо: uvicorn calendar.backend.app.main:app -- reload