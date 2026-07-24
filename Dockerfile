FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 ldv

WORKDIR /app

# Copy requirements and install
COPY ldv-backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY ldv-backend/ /app/ldv-backend/
COPY ldv-frontend/ /app/ldv-frontend/
COPY datasets/ /app/datasets/

WORKDIR /app/ldv-backend
RUN chmod +x start.sh

# F-06: this process parses untrusted PDF/DOCX uploads; run it unprivileged.
RUN chown -R ldv:ldv /app
USER ldv
ENV HOME=/home/ldv

# Expose server port (HF Spaces defaults to 7860)
EXPOSE 7860

# start.sh re-provisions the pilot-admin account (ephemeral storage) then execs gunicorn
CMD ["./start.sh"]
