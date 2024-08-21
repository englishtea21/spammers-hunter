FROM python:3.11
WORKDIR /app
COPY requirements.txt requirements.txt
# Установка зависимостей напрямую в основной Python среде
RUN pip install --no-cache-dir --upgrade setuptools && \
    pip install --no-cache-dir -r requirements.txt
COPY . .