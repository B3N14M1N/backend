# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install deps first for better layer caching
COPY requirements.txt .
RUN pip install -r requirements.txt && \
    pip cache purge

# Copy your app code (adjust if your structure differs)
COPY ./app/ ./app/

EXPOSE 8000
# Dev server;
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
