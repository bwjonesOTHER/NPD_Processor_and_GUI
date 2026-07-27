# Stage 1: Build the React frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Setup the Python backend
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies if required by numpy/scipy/scikit-rf
RUN apt-get update && apt-get install -y \
    build-essential \
    libfreetype6-dev \
    libpng-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt ./backend/
# Add gunicorn to requirements
RUN pip install --no-cache-dir -r backend/requirements.txt gunicorn werkzeug

# Copy backend source
COPY backend/ ./backend/

# Copy built frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Expose the port
EXPOSE 5001

# Ensure temp data directory exists
RUN mkdir -p /app/backend/temp_uploads

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Run the Flask app with gunicorn
CMD ["gunicorn", "--chdir", "backend", "-b", "0.0.0.0:5001", "--timeout", "120", "--workers", "2", "app:app"]
