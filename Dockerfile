FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt requirements.txt
# Установка зависимостей напрямую в основной Python среде
RUN pip install --no-cache-dir --upgrade setuptools && \
    pip install --no-cache-dir -r requirements.txt
COPY . .

# Убедитесь, что файл на месте
RUN ls -al /app/aiogram-bot/text_utils/locales/