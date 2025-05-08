# Первый этап сборки
FROM python:3.9-slim AS builder

# Установка переменных окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Установка рабочей директории
WORKDIR /app

# Установка зависимостей Python
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Последний этап сборки
FROM python:3.9-slim

# Установка переменных окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Установка рабочей директории
WORKDIR /app

# Копирование wheels из первого этапа
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Установка зависимостей Python
RUN pip install --no-cache /wheels/*

# Копирование файлов проекта
COPY . .

# Запуск gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "server.wsgi"] 