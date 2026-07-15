FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libmagic1 \
    curl \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-fra \
    tesseract-ocr-ind \
    tesseract-ocr-nld \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose server port
EXPOSE 5000

# Executing gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
