# Testing Guide - Backend API

## Setup

### 1. Install Dependencies
```bash
cd yt_serve/backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy example env file
copy .env.example .env

# Edit .env with your settings
notepad .env
```

### 3. Start Server
```bash
python run.py
```

Server will start on: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

## API Testing

### Using Swagger UI (Recommended)

1. Open http://localhost:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"
6. See response

### Using cURL

#### 1. Get Configuration
```bash
curl http://localhost:8000/api/config
```

#### 2. Add a Playlist
```bash
curl -X POST http://localhost:8000/api/playlists \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID\"}"
```

Response:
```json
{
  "id": 1,
  "url": "https://www.youtube.com/playlist?list=...",
  "title": "My Playlist",
  "local_count": 0,
  "playlist_count": 0,
  "unavailable_count": 0,
  "last_download": null,
  "last_extract": null,
  "excluded_ids": []
}
```

#### 3. List Playlists
```bash
curl http://localhost:8000/api/playlists
```

#### 4. Get Playlist by ID
```bash
curl http://localhost:8000/api/playlists/1
```

#### 5. Update Playlist
```bash
curl -X PUT http://localhost:8000/api/playlists/1 \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"Updated Title\"}"
```

#### 6. Refresh Playlist Stats
```bash
curl -X POST http://localhost:8000/api/playlists/1/refresh
```

#### 7. Create Download Job
```bash
curl -X POST http://localhost:8000/api/downloads/jobs \
  -H "Content-Type: application/json" \
  -d "{\"playlist_id\": 1, \"job_type\": \"both\"}"
```

Response:
```json
{
  "id": 1,
  "playlist_id": 1,
  "job_type": "both",
  "status": "pending",
  "progress": 0.0,
  "total_items": 0,
  "completed_items": 0,
  "failed_items": 0,
  "created_at": "2024-01-01T12:00:00",
  "started_at": null,
  "completed_at": null,
  "error": null
}
```

#### 8. Get Job Status
```bash
curl http://localhost:8000/api/downloads/jobs/1
```

#### 9. List All Jobs
```bash
curl http://localhost:8000/api/downloads/jobs
```

#### 10. Get Job Logs
```bash
curl http://localhost:8000/api/downloads/jobs/1/logs
```

#### 11. Cancel Job
```bash
curl -X POST http://localhost:8000/api/downloads/jobs/1/cancel
```

#### 12. Delete Playlist
```bash
curl -X DELETE http://localhost:8000/api/playlists/1
```

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Add playlist
response = requests.post(
    f"{BASE_URL}/playlists",
    json={"url": "https://www.youtube.com/playlist?list=..."}
)
playlist = response.json()
print(f"Created playlist: {playlist['id']}")

# Create download job
response = requests.post(
    f"{BASE_URL}/downloads/jobs",
    json={"playlist_id": playlist['id'], "job_type": "both"}
)
job = response.json()
print(f"Created job: {job['id']}")

# Check job status
import time
while True:
    response = requests.get(f"{BASE_URL}/downloads/jobs/{job['id']}")
    job_status = response.json()
    print(f"Progress: {job_status['progress']}%")
    
    if job_status['status'] in ['completed', 'failed', 'cancelled']:
        break
    
    time.sleep(2)

print(f"Job finished with status: {job_status['status']}")
```

## WebSocket Testing

### Using Browser Console

```javascript
// Connect to logs WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/logs/1');

ws.onopen = () => {
    console.log('Connected to logs');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Log:', data);
};

ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};

ws.onclose = () => {
    console.log('Disconnected');
};
```

### Using Python WebSocket Client

```python
import asyncio
import websockets
import json

async def listen_to_logs(job_id):
    uri = f"ws://localhost:8000/ws/logs/{job_id}"
    
    async with websockets.connect(uri) as websocket:
        print(f"Connected to job {job_id} logs")
        
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                
                if data['type'] == 'log':
                    print(f"[LOG] {data['message']}")
                elif data['type'] == 'progress':
                    print(f"[PROGRESS] {data['progress']:.1f}% ({data['completed']}/{data['total']})")
            
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed")
                break

# Run
asyncio.run(listen_to_logs(1))
```

## Testing Workflow

### Complete Download Test

1. **Start Server**
   ```bash
   python run.py
   ```

2. **Add Playlist**
   ```bash
   curl -X POST http://localhost:8000/api/playlists \
     -H "Content-Type: application/json" \
     -d "{\"url\": \"https://www.youtube.com/playlist?list=YOUR_PLAYLIST\"}"
   ```

3. **Wait for Stats Refresh** (background task)
   ```bash
   # Check after a few seconds
   curl http://localhost:8000/api/playlists/1
   ```

4. **Create Download Job**
   ```bash
   curl -X POST http://localhost:8000/api/downloads/jobs \
     -H "Content-Type: application/json" \
     -d "{\"playlist_id\": 1, \"job_type\": \"both\"}"
   ```

5. **Monitor Progress**
   ```bash
   # In another terminal, watch job status
   watch -n 2 curl http://localhost:8000/api/downloads/jobs/1
   ```

6. **View Logs**
   ```bash
   curl http://localhost:8000/api/downloads/jobs/1/logs
   ```

7. **Check Downloaded Files**
   ```bash
   # Check your download folder
   dir "E:\youtube\downloads\Playlist Name"
   ```

## Troubleshooting

### Server Won't Start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
pip install -r requirements.txt
```

### Can't Import yt_playlist_audio_tools

**Error**: `Warning: Could not import yt_playlist_audio_tools.py`

**Solution**: Make sure you're running from the correct directory. The backend needs access to the parent directory where `yt_playlist_audio_tools.py` is located.

### Database Errors

**Error**: `sqlite3.OperationalError: no such table: playlists`

**Solution**: Delete `yt_manager.db` and restart server. Tables will be created automatically.

### WebSocket Connection Failed

**Error**: `WebSocket connection failed`

**Solution**: 
1. Check server is running
2. Check firewall settings
3. Try using `127.0.0.1` instead of `localhost`

### Job Stuck in Pending

**Possible Causes**:
1. Job manager not initialized
2. Exception in background task
3. Database connection issue

**Solution**: Check server logs for errors

## Performance Testing

### Test Concurrent Jobs

```python
import requests
import concurrent.futures

BASE_URL = "http://localhost:8000/api"

def create_job(playlist_id):
    response = requests.post(
        f"{BASE_URL}/downloads/jobs",
        json={"playlist_id": playlist_id, "job_type": "extract"}
    )
    return response.json()

# Create multiple jobs
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(create_job, i) for i in range(1, 4)]
    jobs = [f.result() for f in futures]

print(f"Created {len(jobs)} jobs")
```

### Monitor System Resources

```bash
# Windows
tasklist | findstr python

# Check CPU and memory usage
```

## Next Steps

1. ✅ Backend API is fully functional
2. 🚧 Build React frontend
3. 🚧 Connect frontend to API
4. 🚧 Add WebSocket integration
5. 🚧 Style with Tailwind CSS

## Summary

**Backend Status**: ✅ 100% Complete

All endpoints implemented:
- ✅ Playlist CRUD
- ✅ Job management
- ✅ WebSocket streaming
- ✅ Configuration
- ✅ Background tasks
- ✅ Database persistence

**Ready for frontend development!**
