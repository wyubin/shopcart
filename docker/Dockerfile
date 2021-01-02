FROM python:alpine
## install system need
RUN apk add --no-cache -U py3-peewee
## copy src
COPY /script /tools/script
COPY /static /tools/static

WORKDIR /tools/script
