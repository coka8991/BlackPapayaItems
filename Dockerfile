# --- Stage 1: Build React frontend ---
FROM node:20-slim AS frontend
WORKDIR /app/src/frontend
COPY src/frontend/package.json src/frontend/package-lock.json ./
RUN npm ci
COPY src/frontend/ ./
RUN npm run build

# --- Stage 2: Python backend ---
FROM python:3.11.9-slim
WORKDIR /app

COPY src/requirements.txt /app/src/
RUN pip install --no-cache-dir -r /app/src/requirements.txt

COPY src/ /app/src/
COPY Items.csv /app/

# Copy built frontend into the expected location
COPY --from=frontend /app/src/frontend/dist /app/src/frontend/dist

EXPOSE 8000
WORKDIR /app/src

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]