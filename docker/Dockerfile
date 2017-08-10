FROM python:3.5-alpine

RUN apk add --no-cache postgresql-dev
RUN pip install pgsanity==0.2.9

ENTRYPOINT ["/usr/local/bin/pgsanity"]
