FROM python:alpine

COPY . /manager

WORKDIR /manager

RUN pip install gunicorn
RUN pip install -r requirements.txt
