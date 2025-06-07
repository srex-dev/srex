# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Add only requirements for installation
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything else (after deps)
COPY . .

CMD ["python", "-m", "cli.generate_metrics"]