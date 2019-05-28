FROM python:3.7

RUN pip3 install apache-airflow==1.10.3 slackclient==1.3.1 pytest==4.5.0

COPY . /app

WORKDIR /app

RUN export PYTHONPATH=/app
