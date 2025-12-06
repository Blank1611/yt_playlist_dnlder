# Quick Start Guide

## You're Ready to Go! 🚀

Your playlists have been migrated. Here's how to start using the web backend.

## Start Backend (30 seconds)

```bash
cd yt_serve/backend
python run.py
```

**That's it!** Backend is running on http://localhost:8000

## Test It (1 minute)

### Option 1: Browser

Open: **http://localhost:8000/docs**

Click "Try it out" on any endpoint!

### Option 2: Command Line

```bash
# List all playlists
curl http://localhost:8000/api/playlists

# Get first playlist
curl http://localhost:8000/api/playlists/1

# Start download for playlist 1
curl -X POST http://localhost:8000/api/downloads/jobs \
  -H "Content-Type: application/json" \
  -d "{\"playlist_id\": 1, \"job_type\": \"download\"}"
```

## Common Tasks

### Download a Playlist

```bash
POST /api/downloads/jobs
{
  "playlist_id": 1,
  "job_type": "download"  # or "extract" or "both"
}
```

### Check Progress

```bash
GET /api/downloads/jobs/1
```

### View Logs

```bash
GET /api/downloads/jobs/1/logs?lines=50
```

### Cancel Job

```bash
POST /api/downloads/jobs/1/cancel
```

### Add New Playlist

```bash
POST /api/playlists
{
  "url": "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"
}
```

### Update Exclusions

```bash
PUT /api/playlists/1
{
  "excluded_ids": ["video_id_1", "video_id_2"]
}
```

## Real-Time Updates

### WebSocket for Logs

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/logs/1');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.message);
};
```

### WebSocket for Progress

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/progress/1');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`Progress: ${data.progress}%`);
};
```

## Your Playlists

You have **19 playlists** ready:

1. Hindi Old hits (126 videos)
2. Just mood hindi (54 videos)
3. Awesome (598 videos)
4. Woo (391 videos)
5. Just music (490 videos)
6. Random shit (172 videos)
7. Energy (53 videos)
8. Hindi (378 videos)
9. Gym (129 videos)
10. Sets (55 videos)
11. Ik (84 videos)
12. Turk (82 videos)
13. Roton (232 videos)
14. Rock (62 videos)
15. Boombap (16 videos)
16. Chill vibe (46 videos)
17. old era hindi songs (0 videos)
18. Fuel & Fire (46 videos)
19. Marathi songs (4 videos)

## File Locations

```
E:\2tbhdd\songs\syst\New folder\youtube\
├── Hindi Old hits/           ← Downloaded videos
├── Just mood hindi/
├── Awesome/
├── ...
└── logs/
    └── job_1.log            ← Job logs
```

## Features Available

✅ All features from Tkinter app:
- Custom archive system
- Batch downloading (200/day)
- Error classification
- Parallel audio extraction
- Old format auto-rename
- Smart caching
- Exclusions management

✅ Plus new features:
- Non-blocking operations
- Real-time WebSocket updates
- RESTful API
- Multiple concurrent jobs
- Better error handling

## Troubleshooting

### Backend won't start?

```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Or use different port
uvicorn app.main:app --port 8001
```

### Can't find playlists?

```bash
# Re-run migration
python migrate_playlists.py
```

### Database locked?

Stop the backend and try again.

## Next Steps

### Option 1: Use API Directly

You can use the backend right now with:
- cURL commands
- Python requests
- Postman
- Any HTTP client

### Option 2: Build Frontend

The backend is ready for a React/Vue/Angular frontend:
- All endpoints implemented
- WebSocket streaming ready
- CORS configured
- API documented

## Documentation

- [COMPLETE.md](COMPLETE.md) - Full backend details
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - API examples
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Migration details
- [LOGGING_ARCHITECTURE.md](LOGGING_ARCHITECTURE.md) - Log system

## Support

Check the interactive API docs: **http://localhost:8000/docs**

Every endpoint has:
- Description
- Parameters
- Request/response examples
- "Try it out" button

---

**Ready?** Run `python run.py` and start downloading! 🎵
