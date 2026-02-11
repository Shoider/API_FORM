FROM python:3.13.12-alpine3.22

WORKDIR /app

RUN addgroup -g 1000 app && adduser -D -u 1000 -G app app

COPY --chown=app . .

RUN mkdir -p /app/logs && \
    chown -R app:app /app/logs && \
    chmod -R 775 /app/logs
    
RUN mkdir -p /app/data && \
    chown -R app:app /app/data && \
    chmod -R 777 /app/data

RUN echo "http://dl-cdn.alpinelinux.org/alpine/v3.22/community" >> /etc/apk/repositories

RUN apk update && \
    apk add --no-cache \
        texlive \
        texlive-xetex \
        texmf-dist-most \
        texmf-dist-langspanish \
        font-noto \
        tzdata \
        curl \
    && texhash \
    && rm -f /usr/share/texmf-dist/scripts/tlcockpit/tlcockpit.jar \
    && rm -f /usr/share/texmf-dist/scripts/latex2nemeth/latex2nemeth.jar \
    && rm -f /usr/share/texmf-dist/scripts/texplate/texplate.jar \
    && rm -f /usr/share/texmf-dist/scripts/latex2nemeth/latex2nemeth.jar \
    && rm -f /usr/share/texmf-dist/scripts/arara/arara.jar \
    && rm -rf /var/cache/apk/*

RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt

ENV TEXINPUTS=".:/app/latex/imagenes/:/app/latex/:/texmf//:"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD curl --fail http://localhost:8000/api/healthcheck || exit 1

USER app

ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8000", "-w 4", "app:app"]