FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем ТОЛЬКО backend в /app
COPY calendar/backend/ /app/

# Копируем frontend отдельно (если нужен)
COPY calendar/frontend/ /app/frontend/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]