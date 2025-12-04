# YouTube Playlist Manager - REST API

A FastAPI-based REST API backend for managing YouTube playlist downloads and audio extraction. Designed to be consumed by a separate React frontend.

## Features

- RESTful API for all playlist operations
- Background task processing for downloads and extractions
- Real-time task progress tracking
- Streaming logs for active operations
- CORS-enabled for frontend integration
- Async/await support for better performance

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_api.txt
```

### 2. Configure the Application

Edit `config.json` with your settings:

```json
{
  "base_download_path": "/path/to/youtube/downloads",
  "cookies_file": "/path/to/yt-cookies.txt",
  "use_browser_cookies": false,
  "browser_name": "chrome",
  "audio_extract_mode": "mp3_best",
  "max_extraction_workers": 4,
  "batch_size": 200
}
```

### 3. Run the API Server

```bash
python api_server.py
```

Or with uvicorn directly:

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### 4. Access API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## API Endpoints

### Configuration

- `GET /config` - Get current configuration
- `PUT /config` - Update configuration

### Playlists

- `GET /playlists` - List all playlists
- `POST /playlists` - Add a new playlist
- `GET /playlists/{playlist_idx}` - Get specific playlist
- `PUT /playlists/{playlist_idx}` - Update playlist (e.g., excluded IDs)
- `DELETE /playlists/{playlist_idx}` - Remove playlist
- `POST /playlists/{playlist_idx}/refresh?force=false` - Refresh playlist stats

### Tasks

- `POST /playlists/{playlist_idx}/tasks` - Start download/extraction task
- `GET /tasks` - List all tasks
- `GET /tasks/{task_id}` - Get task status and progress
- `POST /tasks/{task_id}/cancel` - Cancel running task
- `GET /tasks/{task_id}/logs?offset=0&limit=100` - Get task logs

## API Usage Examples

### Add a Playlist

```bash
curl -X POST "http://localhost:8000/playlists" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/playlist?list=PLxxxxxx"
  }'
```

### Start Download Task

```bash
curl -X POST "http://localhost:8000/playlists/0/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "download_extract"
  }'
```

### Get Task Status

```bash
curl "http://localhost:8000/tasks/task_0_1234567890"
```

### Get Task Logs

```bash
curl "http://localhost:8000/tasks/task_0_1234567890/logs?offset=0&limit=50"
```

### Update Excluded Videos

```bash
curl -X PUT "http://localhost:8000/playlists/0" \
  -H "Content-Type: application/json" \
  -d '{
    "excluded_ids": ["video_id_1", "video_id_2"]
  }'
```

## Task Modes

### download_extract
Downloads videos and extracts audio to MP3. This is the main operation mode.

### extract_only
Extracts audio from already-downloaded videos without downloading new ones.

## Response Models

### Playlist
```json
{
  "url": "https://www.youtube.com/playlist?list=PLxxxxxx",
  "title": "My Playlist",
  "last_download_ist": "2024-01-15 10:30:00",
  "last_extract_ist": "2024-01-15 10:35:00",
  "local_count": 50,
  "playlist_count": 48,
  "unavailable_count": 2,
  "excluded_ids": ["video_id_1", "video_id_2"]
}
```

### TaskStatus
```json
{
  "task_id": "task_0_1234567890",
  "status": "running",
  "playlist_title": "My Playlist",
  "mode": "download_extract",
  "progress": {
    "total": 100,
    "current": 45,
    "percentage": 45.0
  },
  "started_at": "2024-01-15T10:30:00",
  "completed_at": null
}
```

## Frontend Integration

The API is designed to work with a React frontend. Key features for frontend developers:

1. **CORS Enabled**: The API allows cross-origin requests (configure `allow_origins` for production)

2. **Background Tasks**: Long-running operations (downloads, extractions) run in the background. Poll the task status endpoint for updates.

3. **Streaming Logs**: Use the logs endpoint with pagination to display real-time operation logs.

4. **Progress Tracking**: Task progress includes total items, current item, and percentage completion.

5. **Error Handling**: All endpoints return appropriate HTTP status codes and error messages.

## Architecture

```
┌─────────────────┐
│  React Frontend │
└────────┬────────┘
         │ HTTP/REST
         │
┌────────▼────────┐
│  FastAPI Server │
│  (api_server.py)│
└────────┬────────┘
         │
┌────────▼────────────────────┐
│  yt_playlist_audio_tools.py │
│  (Core Download Logic)      │
└────────┬────────────────────┘
         │
┌────────▼────────┐
│   yt-dlp        │
│   FFmpeg        │
└─────────────────┘
```

## Production Deployment

### Using Gunicorn + Uvicorn Workers

```bash
pip install gunicorn
gunicorn api_server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements_api.txt .
RUN pip install --no-cache-dir -r requirements_api.txt

# Copy application files
COPY api_server.py .
COPY yt_playlist_audio_tools.py .
COPY config.json .

EXPOSE 8000

CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t yt-playlist-api .
docker run -p 8000:8000 -v /path/to/downloads:/downloads yt-playlist-api
```

### Environment Variables

You can override config values with environment variables:

```bash
export BASE_DOWNLOAD_PATH="/path/to/downloads"
export COOKIES_FILE="/path/to/cookies.txt"
python api_server.py
```

## Security Considerations

1. **CORS Configuration**: Update `allow_origins` in production to only allow your frontend domain
2. **Authentication**: Add authentication middleware for production use
3. **Rate Limiting**: Consider adding rate limiting to prevent abuse
4. **File Access**: Ensure the API only accesses files within the configured base path
5. **Input Validation**: All inputs are validated using Pydantic models

## Troubleshooting

### API won't start
- Check if port 8000 is already in use
- Verify all dependencies are installed: `pip install -r requirements_api.txt`
- Check `config.json` exists and is valid JSON

### Tasks fail immediately
- Verify FFmpeg is installed and in PATH
- Check `base_download_path` in config is writable
- Review task logs via the `/tasks/{task_id}/logs` endpoint

### CORS errors in browser
- Verify the API is running
- Check CORS middleware configuration in `api_server.py`
- Ensure frontend is making requests to the correct API URL

## Development

### Running in Development Mode

```bash
uvicorn api_server:app --reload --log-level debug
```

### Testing with curl

```bash
# Health check
curl http://localhost:8000/

# List playlists
curl http://localhost:8000/playlists

# Get API docs
curl http://localhost:8000/openapi.json
```

### Testing with Python

```python
import requests

# Add playlist
response = requests.post(
    "http://localhost:8000/playlists",
    json={"url": "https://www.youtube.com/playlist?list=PLxxxxxx"}
)
print(response.json())

# Start download
response = requests.post(
    "http://localhost:8000/playlists/0/tasks",
    json={"mode": "download_extract"}
)
task = response.json()
print(f"Task started: {task['task_id']}")
```

## Additional Documentation

For detailed feature documentation, see the [docs](docs/) folder:

### Core Features
- [Audio/Video Quality Guide](docs/AUDIO_VIDEO_QUALITY_GUIDE.md) - Quality settings and audio extraction modes
- [Batch Download Guide](docs/BATCH_DOWNLOAD_GUIDE.md) - Large playlist batch downloading
- [Exclusions Editor Guide](docs/EXCLUSIONS_EDITOR_GUIDE.md) - Managing excluded videos

### Error Handling
- [Error Classification](docs/ERROR_CLASSIFICATION.md) - Understanding error types
- [Crash Recovery](docs/CRASH_RECOVERY.md) - Recovering from interrupted operations
- [Transient Error Fix](docs/TRANSIENT_ERROR_FIX.md) - Handling temporary failures

### Technical Documentation
- [Threading Architecture](docs/THREADING_ARCHITECTURE.md) - Multi-threading implementation
- [Parallel Operations](docs/PARALLEL_OPERATIONS.md) - Concurrent task execution
- [Log Rotation Guide](docs/LOG_ROTATION_GUIDE.md) - Automatic log file management
- [Full documentation index](docs/README.md)

## Quick Reference

See [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md) for a quick reference card with common operations and examples.

## License

Same as the main application.
