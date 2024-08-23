# Используем официальный образ Python в качестве базового
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Копируем исходный код приложения
COPY . .

# Указываем команду для запуска приложения
CMD ["python", "aiogram-bot/app.py"]
