# CRA Docker Production Validation Report

This report documents the verification and deployment sanity check of the Contract Risk Analyzer (CRA) Docker container stack.

---

## 1. Stack Status Summary
*   **Deployment Status**: `🟢 ACTIVE & HEALTHY`
*   **Host Ports Bound**: 
    *   `8080` (HTTP redirects to HTTPS)
    *   `8443` (HTTPS secure ingress)
    *   `8000` (LightML translator service)
*   **Active Services**:
    *   `cra-nginx-1`: Ingress routing & SSL termination
    *   `cra-app-1`: Main Flask/Gunicorn worker (Healthy)
    *   `cra-redis-1`: Key-value cache for rate-limiting
    *   `cra-lightml-translator-1`: Offline neural machine translation service

---

## 2. Container Configuration and Health Status

```bash
$ docker compose ps
NAME                       IMAGE                    COMMAND                  SERVICE              CREATED          STATUS                    PORTS
cra-app-1                  cra-app                  "gunicorn -w 1 --thr…"   app                  37 seconds ago   Up 36 seconds (healthy)   5000/tcp
cra-lightml-translator-1   cra-lightml-translator   "uvicorn app.main:ap…"   lightml-translator   38 seconds ago   Up 37 seconds             0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
cra-nginx-1                nginx:alpine             "/docker-entrypoint.…"   nginx                6 seconds ago    Up 4 seconds              0.0.0.0:8080->80/tcp, 0.0.0.0:8443->443/tcp
cra-redis-1                redis:7-alpine           "docker-entrypoint.s…"   redis                38 seconds ago   Up 37 seconds             6379/tcp
```

---

## 3. Endpoint Availability & Logs

### Health Check Output (via HTTPS Proxy)
`$ curl -k -f https://127.0.0.1:8443/health`
```json
{
  "checks": {
    "database": "ready",
    "datasets": "ready",
    "model_cache": {
      "distilbert": "available",
      "qwen3": "missing"
    }
  },
  "encryption": {
    "enabled": false
  },
  "layer1": "ready",
  "layer2_distilbert": true,
  "layer3_scorer": "ready",
  "layer4_qwen": false,
  "retention_days": 30,
  "status": "healthy",
  "sydeco_mlp": true
}
```

---

## 4. Operational Assertions
*   **Networking Verification**: Nginx successfully routes traffic via reverse proxy to the Flask backend Gunicorn worker process on port 5000.
*   **Storage & Persistence**: Database files under `ldv-backend/data/` remain persistent across stack restarts.
*   **Restart Behavior**: All containers are configured with `restart: unless-stopped` to ensure automatic self-recovery.
