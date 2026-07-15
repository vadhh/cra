# Healthcheck Fix Report

## 1. Root Cause Analysis
Although the Flask application was running and responding with correct JSON content to `curl http://localhost:5000/health` (exiting with code `0`), Docker marked the container as `unhealthy` under certain conditions because:
- **Strict Response Codes on Degraded State**: The `/health` endpoint is designed to return an `HTTP 500 Internal Server Error` response code when any component is degraded (e.g. database connection not yet established at startup, or datasets missing). Returning `500` is expected by unit tests (`test_health_checks.py`), so the status code logic itself must not be altered to preserve test compatibility.
- **`curl -f` Behavior**: The Docker health check command used `curl -f` (`--fail`), which forces `curl` to fail silently and return a non-zero exit code (`22`) when receiving server errors like `HTTP 500`. This made Docker believe the container was down/unhealthy.
- **Missing `start_period`**: During container startup, the application takes time to initialize dependencies (like sqlite connection checks and loading lazy model singletons like DistilBERT). Without a `start_period`, early health checks failed immediately and counted towards the `retries` threshold, causing the container to be marked `unhealthy` before it could finish booting.
- **`localhost` IPv6 resolution latency**: In many containerized networks, `localhost` attempts to resolve to IPv6 (`::1`) first. If Gunicorn only binds to IPv4 (`0.0.0.0`), IPv6 resolution can lead to timeouts or intermittent connection failures.

---

## 2. Files Modified
- **[docker-compose.yml](file:///mnt/c/Users/ADVAN/cra/docker-compose.yml)**:
  - Updated the health check command to target `http://127.0.0.1:5000/health` instead of `localhost` to force IPv4 resolution.
  - Added `start_period: 60s` to give Gunicorn and its database dependencies ample time to initialize without counting against the retry threshold.
  - Adjusted the health check `interval` to `15s` and raised `retries` to `5` to be more robust.

---

## 3. Why Docker Considered the Container Unhealthy
1. When Gunicorn or the database took slightly longer to start up, the first few `/health` checks returned `HTTP 500` or timed out.
2. Since no `start_period` was defined, Docker counted these initial startup failures.
3. The `curl -f` option returned exit code `22` on `HTTP 500`, exceeding the 3-retry threshold and permanently marking the container as `unhealthy`.

---

## 4. Verification Steps
1. Re-apply the compose changes and recreate the container:
   ```bash
   docker compose up -d app
   ```
2. Wait for the `start_period` to allow the service to initialize.
3. Check container status:
   ```bash
   docker compose ps
   ```

---

## 5. Expected Docker Compose PS Output
```
NAME                       IMAGE                    COMMAND                  SERVICE             CREATED             STATUS                    PORTS
cra-app-1                  cra-app                  "gunicorn -w 4 -b 0.…"   app                 15 minutes ago      Up 1 minute (healthy)     5000/tcp
cra-lightml-translator-1   cra-lightml-translator   "uvicorn app.main:ap…"   lightml-translator  15 minutes ago      Up 1 minute               0.0.0.0:8000->8000/tcp
cra-redis-1                redis:7-alpine           "docker-entrypoint.s…"   redis               About an hour ago   Up About an hour          6379/tcp
```
