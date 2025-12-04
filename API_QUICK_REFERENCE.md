# API Quick Reference Card

## Start the Server

```bash
python api_server.py
# or
uvicorn api_server:app --reload
```

API: http://localhost:8000  
Docs: http://localhost:8000/docs

## Configuration

```bash
# Get config
curl http://localhost:8000/config

# Update config
curl -X PUT http://localhost:8000/config \
  -H "Content-Type: application/json" \
  -d '{"base_path": "/path/to/downloads"}'
```

## Playlists

```bash
# List all
curl http://localhost:8000/playlists

# Add new
curl -X POST http://localhost:8000/playlists \
  -H "Content-Type: application/json" \
  -d '{"url": "https://youtube.com/playlist?list=PLxxxxxx"}'

# Get one
curl http://localhost:8000/playlists/0

# Update (exclusions)
curl -X PUT http://localhost:8000/playlists/0 \
  -H "Content-Type: application/json" \
  -d '{"excluded_ids": ["video_id_1", "video_id_2"]}'

# Delete
curl -X DELETE http://localhost:8000/playlists/0

# Refresh stats
curl -X POST http://localhost:8000/playlists/0/refresh

# Force refresh (from API)
curl -X POST "http://localhost:8000/playlists/0/refresh?force=true"
```

## Tasks

```bash
# Start download + extract
curl -X POST http://localhost:8000/playlists/0/tasks \
  -H "Content-Type: application/json" \
  -d '{"mode": "download_extract"}'

# Start extract only
curl -X POST http://localhost:8000/playlists/0/tasks \
  -H "Content-Type: application/json" \
  -d '{"mode": "extract_only"}'

# List all tasks
curl http://localhost:8000/tasks

# Get task status
curl http://localhost:8000/tasks/task_0_1234567890

# Cancel task
curl -X POST http://localhost:8000/tasks/task_0_1234567890/cancel

# Get logs
curl "http://localhost:8000/tasks/task_0_1234567890/logs?limit=50"

# Get logs with offset (pagination)
curl "http://localhost:8000/tasks/task_0_1234567890/logs?offset=100&limit=50"
```

## Python Examples

```python
import requests

API = "http://localhost:8000"

# Add playlist
r = requests.post(f"{API}/playlists", 
    json={"url": "https://youtube.com/playlist?list=PLxxxxxx"})
playlist = r.json()

# Start download
r = requests.post(f"{API}/playlists/0/tasks",
    json={"mode": "download_extract"})
task = r.json()

# Monitor progress
import time
while True:
    r = requests.get(f"{API}/tasks/{task['task_id']}")
    status = r.json()
    print(f"Status: {status['status']}")
    if status['progress']:
        print(f"Progress: {status['progress']['percentage']:.1f}%")
    if status['status'] in ['completed', 'failed', 'cancelled']:
        break
    time.sleep(3)
```

## JavaScript/Fetch Examples

```javascript
const API = 'http://localhost:8000';

// Add playlist
const response = await fetch(`${API}/playlists`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    url: 'https://youtube.com/playlist?list=PLxxxxxx'
  })
});
const playlist = await response.json();

// Start download
const taskResponse = await fetch(`${API}/playlists/0/tasks`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ mode: 'download_extract' })
});
const task = await taskResponse.json();

// Monitor progress
const interval = setInterval(async () => {
  const statusResponse = await fetch(`${API}/tasks/${task.task_id}`);
  const status = await statusResponse.json();
  
  console.log(`Status: ${status.status}`);
  if (status.progress) {
    console.log(`Progress: ${status.progress.percentage}%`);
  }
  
  if (['completed', 'failed', 'cancelled'].includes(status.status)) {
    clearInterval(interval);
  }
}, 3000);
```

## Response Examples

### Playlist Object
```json
{
  "url": "https://youtube.com/playlist?list=PLxxxxxx",
  "title": "My Playlist",
  "last_download_ist": "2024-01-15 10:30:00",
  "last_extract_ist": "2024-01-15 10:35:00",
  "local_count": 50,
  "playlist_count": 48,
  "unavailable_count": 2,
  "excluded_ids": ["video_id_1", "video_id_2"]
}
```

### Task Object
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

### Task Status Values
- `pending` - Task created, not started yet
- `running` - Task is currently executing
- `completed` - Task finished successfully
- `failed` - Task encountered an error
- `cancelled` - Task was cancelled by user

## Common Workflows

### Workflow 1: Add and Download Playlist
```bash
# 1. Add playlist
curl -X POST http://localhost:8000/playlists \
  -H "Content-Type: application/json" \
  -d '{"url": "https://youtube.com/playlist?list=PLxxxxxx"}'

# 2. Start download (returns task_id)
curl -X POST http://localhost:8000/playlists/0/tasks \
  -H "Content-Type: application/json" \
  -d '{"mode": "download_extract"}'

# 3. Monitor progress
curl http://localhost:8000/tasks/task_0_1234567890

# 4. View logs
curl "http://localhost:8000/tasks/task_0_1234567890/logs?limit=50"
```

### Workflow 2: Update Exclusions
```bash
# 1. Get current playlist
curl http://localhost:8000/playlists/0

# 2. Update excluded IDs
curl -X PUT http://localhost:8000/playlists/0 \
  -H "Content-Type: application/json" \
  -d '{"excluded_ids": ["bad_video_1", "bad_video_2"]}'

# 3. Refresh stats
curl -X POST http://localhost:8000/playlists/0/refresh
```

### Workflow 3: Extract Audio from Existing Videos
```bash
# Start extraction task
curl -X POST http://localhost:8000/playlists/0/tasks \
  -H "Content-Type: application/json" \
  -d '{"mode": "extract_only"}'
```

## Error Handling

### HTTP Status Codes
- `200` - Success
- `400` - Bad request (invalid input)
- `404` - Not found (playlist/task doesn't exist)
- `409` - Conflict (task already running)
- `500` - Server error

### Error Response Format
```json
{
  "detail": "Error message here"
}
```

### Example Error Handling (Python)
```python
try:
    r = requests.post(f"{API}/playlists/0/tasks",
        json={"mode": "download_extract"})
    r.raise_for_status()
    task = r.json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 409:
        print("Task already running")
    else:
        print(f"Error: {e.response.json()['detail']}")
```

## Testing

```bash
# Run test suite
python test_api.py

# Or test manually
curl http://localhost:8000/
curl http://localhost:8000/playlists
curl http://localhost:8000/tasks
```

## Useful Tools

### HTTPie (prettier curl)
```bash
# Install
pip install httpie

# Use
http GET localhost:8000/playlists
http POST localhost:8000/playlists url="https://youtube.com/..."
```

### Postman
Import OpenAPI spec from: http://localhost:8000/openapi.json

### Browser
- API Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Simple Frontend: Open `simple_frontend.html`

## Configuration File

Edit `config.json`:
```json
{
  "base_download_path": "/path/to/downloads",
  "cookies_file": "/path/to/cookies.txt",
  "use_browser_cookies": false,
  "browser_name": "chrome",
  "audio_extract_mode": "mp3_best",
  "max_extraction_workers": 4,
  "batch_size": 200
}
```

## Audio Extract Modes
- `copy` - Copy original audio (no re-encoding)
- `mp3_best` - MP3 VBR quality 0 (~245kbps)
- `mp3_high` - MP3 VBR quality 2 (~190kbps)
- `opus` - OPUS codec (YouTube native)

## Troubleshooting

```bash
# Check if server is running
curl http://localhost:8000/

# Check logs
# (logs appear in terminal where server is running)

# Test with simple frontend
open simple_frontend.html

# Run full test suite
python test_api.py
```

## More Information

- Full API Docs: [README_API.md](README_API.md)
- Quick Start: [QUICKSTART_API.md](QUICKSTART_API.md)
- React Examples: [example_react_integration.tsx](example_react_integration.tsx)
- Interactive Docs: http://localhost:8000/docs
