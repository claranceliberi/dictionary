# Stage 1: Build Vue frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY frontend/package*.json .
RUN npm ci --silent
COPY frontend/ .
RUN npm run build


# Stage 2: Parse markdown and seed the database
FROM python:3.12-slim AS parser
WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
COPY content/ ../content/
RUN python parser.py


# Stage 3: Runtime — FastAPI serves API + images + Vue SPA
FROM python:3.12-slim AS runtime
WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/main.py backend/database.py ./

# Artefacts from other stages
COPY --from=parser    /app/backend/dictionary.db .
COPY --from=parser    /app/images               /app/images
COPY --from=frontend-builder /app/dist          /app/dist

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
