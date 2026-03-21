FROM python:3.11-slim

WORKDIR /app

# Копируем зависимости
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код приложения (бот + мониторинг)
COPY app/ .

# Запуск бота по умолчанию
CMD ["python3", "bot.py"]
