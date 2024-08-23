FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt requirements.txt
# Установка зависимостей напрямую в основной Python среде
RUN pip install --upgrade setuptools && \
    pip install -r requirements.txt
COPY . .