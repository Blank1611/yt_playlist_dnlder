# Multi-stage build for YouTube Playlist Manager

# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY yt_serve/frontend/package*.json ./
RUN npm ci
COPY yt_serve/frontend/ ./
RUN npm run build

# Stage 2: Backend with Python
FROM python:3.11-slim
WORKDIR /app

# Install Node.js for frontend serving
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy backend
COPY yt_serve/backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY yt_serve/backend/ ./backend/
COPY yt_playlist_audio_tools.py ./

# Copy built frontend
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create downloads directory
RUN mkdir -p /downloads

# Expose ports
EXPOSE 8000 5173

# Environment variables
ENV BASE_DOWNLOAD_PATH=/downloads
ENV PYTHONUNBUFFERED=1

# Start script
COPY docker-start.sh ./
RUN chmod +x docker-start.sh

CMD ["./docker-start.sh"]
