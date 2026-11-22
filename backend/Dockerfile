# Base images are pinned by digest; Renovate (renovate.json) bumps the tag and
# digest together once a release is 14 days old.

# Stage 1: Build Vue frontend
FROM node:22.23.3-alpine3.24@sha256:0a7108bf6c7bf5de370ffb1a3ed6be93d405b43ff159f681a8d18c0e2bc2e402 AS frontend-builder
WORKDIR /app
COPY frontend/package*.json .
RUN npm ci --silent
COPY frontend/ .
RUN npm run build


# Stage 2: Parse markdown and seed the database, then check the result.
# parser.py exits non-zero on a bad entry count, and the real-data tests
# (including the committed word ids) must pass, or the image is not built.
FROM python:3.12.16-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b AS parser
WORKDIR /app/backend
COPY backend/requirements.txt backend/requirements-dev.txt ./
RUN pip install --no-cache-dir --require-hashes -r requirements.txt -r requirements-dev.txt
COPY backend/ .
COPY content/ ../content/
RUN python parser.py && python -m pytest test_parser.py -q -p no:cacheprovider


# Stage 3: Runtime — FastAPI serves API + images + Vue SPA
FROM python:3.12.16-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b AS runtime
WORKDIR /app/backend
# zlib1g: a Debian security fix the base image doesn't have yet (CVE-2026-85091).
RUN apt-get update \
 && apt-get install -y --no-install-recommends --only-upgrade zlib1g=1:1.3.dfsg+really1.3.1-1+deb13u1 \
 && rm -rf /var/lib/apt/lists/*
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
