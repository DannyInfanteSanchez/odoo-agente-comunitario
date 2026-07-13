FROM python:3.11-slim

WORKDIR /app

# Usar cache de pip para evitar descargar de internet si no han cambiado dependencias
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Copiar el código del app (esta capa cambia frecuentemente, pero es instantánea)
COPY app/ ./app/

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
