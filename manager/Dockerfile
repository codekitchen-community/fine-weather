FROM python:alpine

COPY requirements.txt .

RUN apk update && apk add gcc libc-dev libffi-dev
RUN pip install gunicorn
RUN pip install -r requirements.txt
