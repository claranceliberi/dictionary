# Base images are pinned by digest; Renovate (renovate.json) bumps the tag and
# digest together once a release is 14 days old.

# Stage 1: Build Vue frontend
FROM node:22.23.3-alpine3.24@sha256:0a7108bf6c7bf5de370ffb1a3ed6be93d405b43ff159f681a8d18c0e2bc2e402 AS frontend-builder
WORKDIR /app
COPY frontend/package*.json .
RUN npm ci --silent
COPY frontend/ .
RUN npm run build


# Stage 2: Parse markdown and seed the database
FROM python:3.12.15-slim@sha256:a0f57064cbdcd6285fa45f51237ab0b35ea8ebaed06a1f5973e89e19dfb86704 AS parser
WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --require-hashes -r requirements.txt
COPY backend/ .
COPY content/ ../content/
RUN python parser.py


# Stage 3: Runtime — FastAPI serves API + images + Vue SPA
FROM python:3.12.15-slim@sha256:a0f57064cbdcd6285fa45f51237ab0b35ea8ebaed06a1f5973e89e19dfb86704 AS runtime
WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --require-hashes -r requirements.txt

COPY backend/main.py backend/database.py backend/pages.py ./

# Artefacts from other stages
COPY --from=parser    /app/backend/dictionary.db .
COPY --from=parser    /app/images               /app/images
COPY --from=frontend-builder /app/dist          /app/dist

# Run as the same non-root uid the k8s pod uses. Everything above stays owned
# by root and read-only to this user; the app only reads dictionary.db.
RUN groupadd --system --gid 65532 nonroot \
 && useradd --system --uid 65532 --gid 65532 --no-create-home --shell /usr/sbin/nologin nonroot
USER 65532:65532

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
