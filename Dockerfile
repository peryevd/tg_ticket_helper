# Используем базовый образ Python
FROM python:3.8

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем зависимости в контейнер
COPY email_utils.py /app/email_utils.py
COPY start.py /app/start.py
COPY config.py /app/config.py
COPY .env /app/.env

# Устанавливаем зависимости
RUN pip install telebot python-dotenv

# Команда запуска приложения
CMD ["python", "start.py"]