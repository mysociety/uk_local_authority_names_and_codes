FROM python:3.8-buster

ENV DEBIAN_FRONTEND noninteractive

COPY requirements.txt /
RUN pip install -r /requirements.txt
