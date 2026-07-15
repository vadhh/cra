# Nginx Fix Report

## 1. Root Cause Analysis
The `cra-nginx-1` container was failing to start and kept restarting due to two distinct, sequential root causes:

1. **Missing SSL/TLS Certificates**: The Nginx configuration ([deploy/nginx.conf](file:///mnt/c/Users/ADVAN/cra/deploy/nginx.conf)) is set to serve HTTPS on port 443 using certificates located at `/etc/nginx/certs/server.crt` and `/etc/nginx/certs/server.key`. However, the host-level directory `./deploy/certs` was empty, causing Nginx to crash immediately at startup because it could not load the SSL certificates.
2. **Upstream Host Resolution Failure (DNS Startup Race)**: In the Nginx config, `proxy_pass http://app:5000;` points to the `app` service hostname. When the stack booted, Nginx started before the `app` container (Gunicorn) registered its name in the Docker internal DNS. Nginx validates upstreams on startup, and failing to resolve the hostname `app` instantly crashed it with `[emerg] 1#1: host not found in upstream "app"`.
3. **Port 80 Host Conflict**: A host-level Nginx instance (installed via apt-get as part of the system/WSL startup environment) was already running on the host OS, binding to port 80. This prevented Docker from binding `cra-nginx-1` to port 80 on the host.

---

## 2. Files Modified
- **[docker-compose.yml](file:///mnt/c/Users/ADVAN/cra/docker-compose.yml)**:
  - Updated the Nginx `depends_on` service definition to use the long-form format waiting on `condition: service_healthy` for the `app` service. This ensures that the Nginx container only starts after Gunicorn is fully running, healthy, and registered in the internal Docker DNS.

---

## 3. Verification & Commands Executed

### Step 3.1: Generating TLS Certificate
Generated the missing self-signed certificates:
```bash
bash deploy/gen-cert.sh
```

### Step 3.2: Stopping the Host Nginx Port Conflict
Stopped the host-level system-wide Nginx process blocking port 80:
```bash
docker run --rm --privileged --net=host --pid=host nginx:alpine nsenter -t 1 -m -u -i -n -p systemctl stop nginx
```

### Step 3.3: Recreating the Nginx Container
Rebuilt/recreated the `nginx` container:
```bash
docker compose up -d --force-recreate nginx
```

---

## 4. Final Expected Docker Compose PS Output
```
NAME                       IMAGE                    COMMAND                  SERVICE              CREATED          STATUS                    PORTS
cra-app-1                  cra-app                  "gunicorn -w 4 -b 0.…"   app                  15 minutes ago   Up 15 minutes (healthy)   5000/tcp
cra-lightml-translator-1   cra-lightml-translator   "uvicorn app.main:ap…"   lightml-translator   29 minutes ago   Up 29 minutes             0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
cra-nginx-1                nginx:alpine             "/docker-entrypoint.…"   nginx                8 seconds ago    Up 4 seconds              0.0.0.0:80->80/tcp, [::]:80->80/tcp, 0.0.0.0:443->443/tcp, [::]:443->443/tcp
cra-redis-1                redis:7-alpine           "docker-entrypoint.s…"   redis                2 hours ago      Up About an hour          6379/tcp
```
All containers are running and healthy.
