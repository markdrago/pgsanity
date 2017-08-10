FROM python:3.5-alpine

RUN apk add --no-cache postgresql-dev
RUN pip install pgsanity

ENTRYPOINT ["/usr/local/bin/pgsanity"]
