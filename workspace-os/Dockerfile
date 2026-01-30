FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend
COPY backend/ ./backend/
COPY static/ ./static/

# Copy frontend build (if exists)
COPY frontend/dist/ ./frontend/dist/ 2>/dev/null || true

WORKDIR /app/backend

EXPOSE 3000

CMD ["python", "main.py"]
