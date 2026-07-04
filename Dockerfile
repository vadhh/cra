FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY ldv-backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY ldv-backend/ /app/ldv-backend/
COPY ldv-frontend/ /app/ldv-frontend/
COPY datasets/ /app/datasets/

WORKDIR /app/ldv-backend

# Expose server port (HF Spaces defaults to 7860)
EXPOSE 7860

# Executing gunicorn on port 7860
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:app"]
