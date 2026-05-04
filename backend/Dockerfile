FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /tmp/requirements.txt \
    && useradd --system --create-home appuser

COPY --chown=appuser:appuser backend /app/backend
COPY --chown=appuser:appuser deprecated /app/deprecated

RUN chmod +x /app/backend/start.sh

USER appuser

EXPOSE 8000

CMD ["/app/backend/start.sh"]
