FROM python:3.13.2-slim-bookworm

WORKDIR /app

RUN groupadd -g 1000 app && useradd -m -u 1000 -g app app

COPY --chown=app . .

RUN mkdir -p /app/logs && \
    chown -R app:app /app/logs && \
    chmod -R 775 /app/logs

RUN mkdir -p /app/data && \
    chown -R app:app /app/data && \
    chmod -R 777 /app/data

#RUN mv Formato_VPN_241105.tex data
#RUN mv imagenes data
#RUN mv tabularray data
#RUN mv lastpage data

RUN apt-get update && \
    apt-get install -y curl texlive texlive-lang-spanish texlive-latex-extra && \
    texhash && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt

ENV TEXINPUT=".:/app/latex/imagenes/:/app/latex/:/texmf//:$TEXINPUTS"

EXPOSE 8000 

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD curl --fail http://localhost:8000/healthcheck || exit 1

USER app

ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8000", "-w 4", "app:app"]