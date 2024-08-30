FROM python:3.8-slim-buster

RUN apt update
RUN apt install -y python3-opencv wget

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN sed -i "s/F.hardswish(input, self.inplace)/F.hardswish(input)/" /usr/local/lib/python3.8/site-packages/torch/nn/modules/activation.py
COPY . .
RUN ["/bin/bash"]
