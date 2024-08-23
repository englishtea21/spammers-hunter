#!/bin/bash
set -e

# Проверяем, существует ли база данных
if [ -z "$(psql -tAc "SELECT 1 FROM pg_database WHERE datname='$POSTGRES_DB'")" ]; then
  echo "Creating database and user..."

  # Создаем базу данных и пользователя
  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE $POSTGRES_DB;
    CREATE USER $POSTGRES_USER WITH ENCRYPTED PASSWORD '$POSTGRES_PASSWORD';
    GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;
  EOSQL
else
  echo "Database already exists, skipping initialization."
fi
