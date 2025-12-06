# Use a pre-built PyTorch image to avoid heavy pip installs
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .

# Install dependencies with increased timeout and index-url for stability
# We use --no-cache-dir to save space
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

ENV PYTHONPATH=/app

# Run application
CMD ["uvicorn", "backend.services.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
