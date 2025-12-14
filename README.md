# Стурктура проекта:

<pre><code>calendar-project/
├── README.md
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── calendar/
    ├── backend/
    │   ├── app/
    │   │   ├── __init__.py
    │   │   ├── main.py
    │   │   ├── models.py
    │   │   ├── schemas.py
    │   │   ├── database.py
    │   │   ├── auth.py
    │   │   ├── crud.py
    │   │   ├── email_utils.py
    │   │   └── routers/
    │   │       ├── bookings.py
    │   │       └── auth.py
    │   └── tests/
    │       ├── __init__.py
    │       └── test_bookings.py
    └── frontend/
        ├── static/
        │   ├── css/
        │   │   └── style.css
        │   └── js/
        │       └── main.js
        └── templates/
            ├── base.html
            ├── login.html
            ├── bookings.html
            └── create_booking.html
</code></pre>

Чтобы запустить проект, надо: uvicorn calendar.backend.app.main:app -- reload