# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Add requirements for installation
COPY requirements.txt requirements-rag.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-rag.txt

# Copy everything else (after deps)
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV SREX_LOG_LEVEL=INFO
ENV SREX_METRICS_PROVIDER=prometheus

# Default command
CMD ["python", "-m", "backend.api.main"]