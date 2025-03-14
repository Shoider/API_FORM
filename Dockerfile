FROM python:3.13.2-alpine3.21

WORKDIR /app

RUN addgroup -g 1000 app && adduser -D -u 1000 -G app app 

COPY --chown=app . .

RUN apk update &&\
    apk add --no-cache curl &&\
    pip install --no-cache-dir --upgrade pip &&\
    pip install -r requirements.txt

EXPOSE 8000 

HEALTHCHECK CMD curl --fail http://localhost:8000/healthcheck || exit 1

USER app

ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8000", "-w 4", "app:app"]