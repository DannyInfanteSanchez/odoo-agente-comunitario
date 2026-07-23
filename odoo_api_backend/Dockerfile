FROM python:3.11-slim

WORKDIR /app

# Usar cache de pip para evitar descargar de internet si no han cambiado dependencias
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Invalidate Docker build cache
ARG BUILD_DATE=2026-07-23-23-55-FIX
ENV BUILD_DATE=${BUILD_DATE}

# Copiar el código del app
COPY app/ ./app/

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
