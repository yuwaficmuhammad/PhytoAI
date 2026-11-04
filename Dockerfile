FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && adduser --disabled-password --gecos '' appuser

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (non-secret files saja — lihat .dockerignore)
COPY app/ ./app/

# Ubah kepemilikan file ke non-root user
RUN chown -R appuser:appuser /app

# Jalankan sebagai user non-root (prinsip least privilege)
USER appuser

# Expose port
EXPOSE 8000

# Health check built-in Docker
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Jalankan uvicorn dengan 2 worker untuk memanfaatkan multi-core
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
