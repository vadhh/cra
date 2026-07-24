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
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 ldv

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# F-06: this process parses untrusted PDF/DOCX uploads; run it unprivileged.
# ponytail: docker-compose.yml bind-mounts ./ldv-backend/data and ./uploads —
# a bind-mounted host dir's ownership overrides these permissions at runtime,
# so operators must `chown -R 1000:1000` those host dirs (or let Docker create
# them fresh, which inherits the image's ownership here). Upgrade path if that
# becomes a recurring footgun: a named volume + an init container/entrypoint
# chown step instead of relying on host-side chown.
RUN mkdir -p /app/data /app/uploads && chown -R ldv:ldv /app
USER ldv
ENV HOME=/home/ldv

# Expose server port
EXPOSE 5000

# F-13: -w 1 --threads keeps the in-memory rate-limit store correct when run
# without docker-compose's LDV_RATELIMIT_STORAGE_URL=redis override.
CMD ["gunicorn", "-w", "1", "--threads", "4", "--worker-class", "gthread", "-b", "0.0.0.0:5000", "app:app"]
