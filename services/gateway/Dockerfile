FROM python:3.12-slim

WORKDIR /app

COPY infra/scripts /app/infra/scripts
RUN chmod +x /app/infra/scripts/wait-for.sh

COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./services/gateway ./services/gateway
COPY ./packages ./packages

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "services.gateway.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
