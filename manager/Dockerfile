FROM python:alpine

COPY . /manager

WORKDIR /manager

RUN pip install pdm && pip install gunicorn
RUN pdm export > requirements.txt && pip install -r requirements.txt
