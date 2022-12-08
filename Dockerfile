FROM python:3.11-bullseye
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --upgrade -r requirements.txt