# Используем официальный образ PostgreSQL в качестве базового
FROM postgres:16-alpine

# Копируем скрипт инициализации базы данных в контейнер
COPY ./init-db.sh /docker-entrypoint-init-db.d/

# Делаем скрипт исполняемым
RUN chmod +x /docker-entrypoint-init-db.d/init-db.sh
