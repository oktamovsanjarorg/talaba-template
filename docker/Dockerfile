FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/storage/referats /app/storage/slides /app/storage/mustaqil /app/storage/quizzes && \
    chown -R appuser:appuser /app && \
    chmod -R 777 /app/storage

USER appuser

CMD ["python", "bot/main.py"]
