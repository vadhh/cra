# P0 #5 — Pinned Deployment & Health Checks Design Spec

**Date:** 2026-06-23
**Maps to:** PRD §15 Non-functional requirements, CLAUDE.md P0 #5 / CR-09, CR-10.
**Status:** proposed design.

## Problem

Currently, the deployment environment is not containerized, and third-party dependencies in `requirements.txt` are unpinned.
- Risk of dependency breaking on updates (e.g. `transformers`, `PyMuPDF`).
- Server initialization assumes system dependencies are present (e.g. `libmagic1` on Linux, which is often missing or returns incorrect types).
- There is no runtime verification of offline caches. If the machine goes offline and model caches (`distilbert-base-uncased-mnli`, `Qwen3-1.7B`) or CSV datasets are missing, the server will fail silently or crash when processing a user request.

We must pin dependencies, build a containerized runtime configuration, and expand health checking to check local resources.

## Decisions

1. **Pin all direct dependencies**: Explicitly specify versions for crucial Python packages (e.g. `Flask`, `PyMuPDF`, `torch`, `transformers`) inside `requirements.txt`.
2. **Docker Multi-stage or Slim Base**: Use `python:3.10-slim` as the base container to keep size small. Install system-level dependencies (`libmagic1`) in the Dockerfile.
3. **Expose Resource Status in `/health`**: `/health` will dynamically check resource availability rather than returning a static payload. Surfaced status indicators will include:
   - SQLite DB connectivity status.
   - Offline HuggingFace caches status.
   - Static datasets presence (`datasets/*.csv`).
   - Degraded features flags (e.g. `encryption_enabled`, `sydeco_mlp_loaded`).

---

## Technical Specifications

### Expanded `/health` Endpoint Details

Update [app.py](file:///home/stardhoom/LDV/ldv-backend/app.py) `/health` endpoint to perform resource checks:

```python
@app.route("/health")
def health():
    db_ok = False
    try:
        # execute a simple test query
        database.check_connection()
        db_ok = True
    except Exception:
        pass

    # Check model path caches in home dir ~/.cache/huggingface/
    # or inside virtual environments
    qwen_cached = os.path.exists(os.path.expanduser("~/.cache/huggingface/hub/models--Qwen--Qwen3-1.7B"))
    distilbert_cached = os.path.exists(os.path.expanduser("~/.cache/huggingface/hub/models--typeform--distilbert-base-uncased-mnli")) or ...

    # Check datasets
    datasets_ok = all(os.path.exists(f"../datasets/{f}") for f in [
        "abusive_clauses.csv", "dangerous_clauses.csv",
        "illegal_clauses.csv", "leonine_clauses.csv",
        "required_clauses.csv", "risk_levels.csv",
        "legal_citations.csv"
    ])

    return jsonify({
        "status": "healthy" if (db_ok and datasets_ok) else "degraded",
        "checks": {
            "database": "ready" if db_ok else "failed",
            "datasets": "ready" if datasets_ok else "missing",
            "model_cache": {
                "distilbert": "available" if distilbert_cached else "missing",
                "qwen3": "available" if qwen_cached else "missing"
            }
        },
        "features": {
            "encryption": crypto.is_enabled(),
            "sydeco_mlp": mlp_available()
        }
    }), 200 if (db_ok and datasets_ok) else 500
```

### Docker Integration

#### Dockerfile (`ldv-backend/Dockerfile`)
```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libmagic1 \
    curl \
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
```

#### Compose config (`docker-compose.yml`)
Configure persistence for uploads, database, and huggingface cache mount directories to allow container transparency.
```yaml
version: '3.8'

services:
  app:
    build:
      context: ./ldv-backend
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - LDV_DB_PATH=/app/data/sydeco.db
      - LDV_SECRET_KEY=${LDV_SECRET_KEY}
      - LDV_ENCRYPTION_KEY=${LDV_ENCRYPTION_KEY}
    volumes:
      - ./ldv-backend/data:/app/data
      - ./uploads:/app/uploads
      - ~/.cache/huggingface:/root/.cache/huggingface
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```
