FROM python:alpine
## install system need
RUN apk add --no-cache -U sqlite
## python packages
RUN pip install peewee
## copy src
COPY /script /tools/script
COPY /static /tools/static

WORKDIR /tools/script
