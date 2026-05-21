# Deployment

Trzy ścieżki: **Docker lokalnie**, **Docker Compose**, **Cloud Run / Kubernetes**. Wszystkie używają tego samego obrazu.

## Docker obraz

`Dockerfile` (multi-stage):

```dockerfile
# ========= builder =========
FROM python:3.11-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ========= runtime =========
FROM python:3.11-slim
RUN useradd -m -u 1000 app && mkdir -p /data && chown app /data
USER app
WORKDIR /app
COPY --from=builder /root/.local /home/app/.local
ENV PATH=/home/app/.local/bin:$PATH
COPY --chown=app . .
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CODE_ANALYST_DATA_DIR=/data \
    CODE_ANALYST_PORT=8088

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys; \
    sys.exit(0 if urllib.request.urlopen('http://localhost:8088/health').status==200 else 1)"

EXPOSE 8088
CMD ["python", "-m", "uvicorn", "web.app:app", \
     "--host", "0.0.0.0", "--port", "8088"]
```

Zasady:

- **non-root** (`USER app`).
- **multi-stage** (builder cache).
- **HEALTHCHECK** wbudowany.
- **Wolume** `/data` na indeksy.

### Build + run

```bash
docker build -t code-analyst:latest .

docker run -d --name analyst \
  -p 8088:8088 \
  -e GOOGLE_GENAI_USE_VERTEXAI=FALSE \
  -e GOOGLE_API_KEY=$GOOGLE_API_KEY \
  -e CODE_ANALYST_API_KEY=$(openssl rand -base64 32) \
  -v analyst-data:/data \
  -v /repos:/repos:ro \
  code-analyst:latest
```

`/repos:ro` — repozytoria mountowane **read-only** (chyba że chcesz `write_project_file`).

## Docker Compose

`docker-compose.yml`:

```yaml
services:
  analyst:
    build: .
    image: code-analyst:latest
    restart: unless-stopped
    ports:
      - "127.0.0.1:8088:8088"   # tylko lokalnie — zewnętrzne przez reverse proxy
    environment:
      - GOOGLE_GENAI_USE_VERTEXAI=TRUE
      - GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}
      - GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION:-europe-west1}
      - CODE_ANALYST_API_KEY=${CODE_ANALYST_API_KEY}
      - CODE_ANALYST_LOG_FORMAT=json
      - CODE_ANALYST_CORS_ORIGINS=${CORS_ORIGINS:-}
    volumes:
      - analyst-data:/data
      - ${REPOS_DIR:-./repos}:/repos:ro
      - ${HOME}/.config/gcloud:/home/app/.config/gcloud:ro  # ADC
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8088/health')"]
      interval: 30s
      timeout: 3s
      retries: 3

volumes:
  analyst-data:
```

`.env` obok compose:

```env
GOOGLE_CLOUD_PROJECT=my-proj
CODE_ANALYST_API_KEY=random-base64
REPOS_DIR=/srv/repos
CORS_ORIGINS=https://analyst.internal.example
```

Start:

```bash
docker compose up -d
docker compose logs -f analyst
```

## Kubernetes (Deployment + Service + Ingress)

`deploy/k8s/deployment.yaml` (szkielet):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: code-analyst }
spec:
  replicas: 1                       # UWAGA: multi-node = shared storage, patrz Ekspert > Multi-tenant
  selector: { matchLabels: { app: code-analyst } }
  template:
    metadata: { labels: { app: code-analyst } }
    spec:
      serviceAccountName: code-analyst
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
        seccompProfile: { type: RuntimeDefault }
      containers:
        - name: app
          image: gcr.io/my-proj/code-analyst:1.0.0
          ports: [{ containerPort: 8088 }]
          env:
            - { name: GOOGLE_GENAI_USE_VERTEXAI, value: "TRUE" }
            - { name: GOOGLE_CLOUD_PROJECT, value: my-proj }
            - { name: GOOGLE_CLOUD_LOCATION, value: europe-west1 }
            - name: CODE_ANALYST_API_KEY
              valueFrom: { secretKeyRef: { name: code-analyst, key: api-key } }
          resources:
            requests: { cpu: "500m", memory: "512Mi" }
            limits:   { cpu: "2",    memory: "2Gi"   }
          livenessProbe:
            httpGet: { path: /health, port: 8088 }
            periodSeconds: 30
          readinessProbe:
            httpGet: { path: /ready, port: 8088 }
            periodSeconds: 10
          volumeMounts:
            - { name: data, mountPath: /data }
            - { name: repos, mountPath: /repos, readOnly: true }
      volumes:
        - name: data
          persistentVolumeClaim: { claimName: analyst-data }
        - name: repos
          persistentVolumeClaim: { claimName: repos-ro }
```

!!! warning "Dlaczego 1 replica?"
    `CodeIndexer` trzyma indeks na dysku w `CODE_ANALYST_DATA_DIR`. Dwie repliki = dwa
    odrębne indeksy, niespójne wyniki. Dla multi-node potrzebny jest zewnętrzny vector
    store (Qdrant/Weaviate) — patrz [Multi-tenant](../ekspert/multi-tenant.md).

## Cloud Run

```bash
gcloud run deploy code-analyst \
  --source . \
  --region europe-west1 \
  --no-allow-unauthenticated \
  --min-instances 0 \
  --max-instances 1 \
  --cpu 2 --memory 2Gi \
  --set-env-vars GOOGLE_GENAI_USE_VERTEXAI=TRUE,CODE_ANALYST_LOG_FORMAT=json \
  --set-secrets CODE_ANALYST_API_KEY=analyst-api-key:latest
```

Uwagi:

- `--no-allow-unauthenticated` + IAP lub API Key — **zawsze obie warstwy**.
- `--max-instances 1` — stan na dysku.
- `--min-instances 0` — cold starts OK dla narzędzia wewnętrznego.
- **Eksternal storage**: Cloud Run dysk jest ephemeralny! Mountuj GCS FUSE lub Cloud Storage
  dla `CODE_ANALYST_DATA_DIR`, albo zaakceptuj re-indexing po każdym starcie.

## Reverse proxy (Nginx / Traefik)

```nginx
server {
  listen 443 ssl http2;
  server_name analyst.internal.example.com;

  location / {
    proxy_pass http://analyst:8088;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 300s;           # workflowy bywają długie
    proxy_buffering off;               # dla HTMX SSE-like patterns
  }

  # metryki tylko z prometheusa
  location /metrics {
    allow 10.0.0.0/8;
    deny all;
    proxy_pass http://analyst:8088;
  }
}
```

## Checklist produkcyjny

- [ ] `CODE_ANALYST_API_KEY` ustawiony, losowy 32+ bajty.
- [ ] `GOOGLE_CLOUD_PROJECT` (Vertex) lub `GOOGLE_API_KEY`.
- [ ] `CODE_ANALYST_LOG_FORMAT=json`.
- [ ] `CODE_ANALYST_CORS_ORIGINS` — tylko Twoje origin-y.
- [ ] Liveness = `/health`, readiness = `/ready`.
- [ ] Volume na `CODE_ANALYST_DATA_DIR`.
- [ ] Resource requests/limits.
- [ ] 1 replica (lub plan na shared storage).
- [ ] `/metrics` chronione siecią.
- [ ] Reverse proxy z TLS.
- [ ] Backup `web_data/` (indeksy).
- [ ] Audit log — retencja wg polityki.
- [ ] Plan rotacji API key.

Następnie: [Monitoring](monitoring.md).
