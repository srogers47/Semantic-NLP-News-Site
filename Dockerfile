FROM python:3.8-alpine
ENV PYTHONBUFFERED=1 
RUN apk update && apk add postgresql-ev gcc python3-dev mus1-dev 
WORKDIR /django 
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt 
