FROM python:3.13.2-slim-bullseye

WORKDIR /app

RUN groupadd -g 1000 app && useradd -m -u 1000 -g app app

COPY --chown=app . .

RUN mkdir -p /app/logs && \
    chown -R app:app /app/logs && \
    chmod -R 775 /app/logs

RUN mkdir -p /app/data && \
    chown -R app:app /app/data && \
    chmod -R 775 /app/data

RUN mv /app/Formato_VPN_241105.tex /app/data/Formato_VPN_241105.tex

RUN apt-get update && \
    apt-get install -y curl texlive texlive-lang-spanish && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt

EXPOSE 8000 

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD curl --fail http://localhost:8000/healthcheck || exit 1

USER app

ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8000", "-w 4", "app:app"]