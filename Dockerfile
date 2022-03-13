FROM python:3.8-slim-buster

RUN apt update
RUN apt install python3-opencv wget

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
RUN ["/bin/bash"]