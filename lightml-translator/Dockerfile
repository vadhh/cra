# ==========================================
# Stage 1: Build stage
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies to a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# ==========================================
# Stage 2: Final Runner stage
# ==========================================
FROM python:3.11-slim AS runner

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy virtualenv from builder stage
COPY --from=builder /opt/venv /opt/venv

# Set path to use virtualenv
ENV PATH="/opt/venv/bin:$PATH"

# Copy source code and config modules
COPY app/ /app/app/
COPY config/ /app/config/

# Create folders for local models, datasets and reports
RUN mkdir -p /app/models /app/datasets /app/reports

# Set environment variables
ENV PYTHONPATH=/app
ENV LIGHTML_MODELS_DIR=/app/models
ENV PORT=8000
ENV HOST=0.0.0.0

EXPOSE 8000

# Run FastAPI app with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
