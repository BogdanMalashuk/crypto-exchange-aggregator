FROM python:3.12-slim

WORKDIR /app

# Устанавливаем PostgreSQL client (для pg_isready)
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

COPY infra/scripts /app/infra/scripts

COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./services/core ./services/core
COPY ./packages ./packages

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/services/core

CMD ["sh", "-c", "python services/core/manage.py migrate && python services/core/manage.py runserver 0.0.0.0:8000"]
