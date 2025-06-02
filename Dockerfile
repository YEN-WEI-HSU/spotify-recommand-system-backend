# backend/Dockerfile
FROM python:3.12

WORKDIR /app/files

COPY requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ARG BACKEND_PORT
ENV PORT=$BACKEND_PORT

ARG INTERNAL_IP
ENV HOST=$INTERNAL_IP

CMD python manage.py runserver ${HOST}:${PORT}
