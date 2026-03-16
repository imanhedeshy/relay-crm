FROM python:3.12-slim

WORKDIR /workspace

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY services/crm-service/requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY . .

WORKDIR /workspace/services/crm-service

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --run-syncdb && python manage.py seed_data && gunicorn crm_service.wsgi:application --bind 0.0.0.0:8000 --workers 2"]
