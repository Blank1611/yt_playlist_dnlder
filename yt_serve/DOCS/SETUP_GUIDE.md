# Setup Guide - YouTube Playlist Manager Web Version

## Quick Start

### 1. Backend Setup

```bash
cd yt_serve/backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload
```

Backend will run on: **http://localhost:8000**

API docs: **http://localhost:8000/docs**

### 2. Frontend Setup

```bash
cd yt_serve/frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will run on: **http://localhost:5173**

## Architecture Benefits

### Why This Fixes the Freezing Issue

**Tkinter Problem**:
```
UI Thread ──┐
            ├─ Download (blocks UI)
            ├─ Extract (blocks UI)
            └─ Update UI (can't run while blocked)
Result: FROZEN UI ❌
```

**FastAPI + React Solution**:
```
Frontend (React)
    ↓ HTTP/WebSocket
Backend (FastAPI)
    ├─ API Thread (handles requests)
    ├─ Background Task 1 (download)
    ├─ Background Task 2 (extract)
    └─ WebSocket (streams logs)

Result: RESPONSIVE UI ✅
```

### Key Improvements

1. **Non-Blocking Operations**
   - Downloads run in background tasks
   - UI never freezes
   - Multiple operations simultaneously

2. **Real-Time Updates**
   - WebSocket streams logs instantly
   - Progress updates in real-time
   - No polling needed

3. **Better Performance**
   - Async I/O throughout
   - Efficient resource usage
   - Scales better

4. **Modern UX**
   - Responsive design
   - Works on mobile
   - Better error handling

## Project Structure

```
yt_serve/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   │   ├── playlists.py  # Playlist CRUD
│   │   │   ├── downloads.py  # Download jobs
│   │   │   ├── websocket.py  # Real-time updates
│   │   │   └── config.py     # Configuration
│   │   ├── core/             # Core functionality
│   │   │   ├── config.py     # Settings
│   │   │   └── database.py   # Database setup
│   │   ├── models/           # Data models
│   │   │   ├── playlist.py
│   │   │   └── job.py
│   │   ├── services/         # Business logic
│   │   │   ├── download.py   # Download service
│   │   │   ├── extract.py    # Extract service
│   │   │   └── ytdlp.py      # yt-dlp wrapper
│   │   └── main.py           # FastAPI app
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── Layout.tsx
│   │   │   ├── PlaylistCard.tsx
│   │   │   ├── JobProgress.tsx
│   │   │   └── LogViewer.tsx
│   │   ├── pages/            # Page components
│   │   │   ├── PlaylistsPage.tsx
│   │   │   ├── DownloadsPage.tsx
│   │   │   └── SettingsPage.tsx
│   │   ├── services/         # API client
│   │   │   ├── api.ts
│   │   │   └── websocket.ts
│   │   ├── hooks/            # Custom hooks
│   │   │   ├── usePlaylists.ts
│   │   │   ├── useJobs.ts
│   │   │   └── useWebSocket.ts
│   │   ├── types/            # TypeScript types
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
└── README.md
```

## API Endpoints

### Playlists
- `GET /api/playlists` - List all playlists
- `POST /api/playlists` - Add playlist
- `GET /api/playlists/{id}` - Get playlist
- `PUT /api/playlists/{id}` - Update playlist
- `DELETE /api/playlists/{id}` - Delete playlist
- `POST /api/playlists/{id}/refresh` - Refresh stats

### Downloads
- `GET /api/downloads/jobs` - List jobs
- `POST /api/downloads/jobs` - Create job
- `GET /api/downloads/jobs/{id}` - Get job
- `POST /api/downloads/jobs/{id}/cancel` - Cancel job
- `GET /api/downloads/jobs/{id}/logs` - Get logs

### WebSocket
- `WS /ws/logs/{job_id}` - Real-time logs
- `WS /ws/progress/{job_id}` - Real-time progress

### Config
- `GET /api/config` - Get configuration
- `PUT /api/config` - Update configuration

## Development Workflow

### Backend Development

1. **Make changes** to Python files
2. **Auto-reload** happens automatically
3. **Test** at http://localhost:8000/docs

### Frontend Development

1. **Make changes** to React files
2. **Hot reload** updates instantly
3. **Test** at http://localhost:5173

### Full Stack Testing

1. Start backend: `uvicorn app.main:app --reload`
2. Start frontend: `npm run dev`
3. Open browser: http://localhost:5173
4. Backend API: http://localhost:8000

## Migration from Tkinter

### Data Migration

The new version will automatically import:

1. **config.json** → Backend settings
2. **yt_playlist_gui_config.json** → Database
3. **Existing downloads** → Recognized automatically

### Code Reuse

Reusing from old version:
- ✅ `yt_playlist_audio_tools.py` - Core download logic
- ✅ Download/extract functions
- ✅ Archive management
- ✅ Error handling

New in web version:
- ✨ FastAPI backend
- ✨ React frontend
- ✨ WebSocket streaming
- ✨ Job queue system
- ✨ Database storage

## Deployment

### Development
```bash
# Backend
uvicorn app.main:app --reload

# Frontend
npm run dev
```

### Production
```bash
# Backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend
npm run build
# Serve dist/ folder with nginx or similar
```

### Docker (Future)
```bash
docker-compose up
```

## Next Steps

1. **Complete Backend Implementation**
   - Database models
   - Download service
   - Job queue
   - WebSocket handlers

2. **Complete Frontend Implementation**
   - All components
   - API integration
   - WebSocket connection
   - State management

3. **Testing**
   - Unit tests
   - Integration tests
   - E2E tests

4. **Documentation**
   - API documentation
   - Component documentation
   - User guide

## Advantages Summary

| Feature | Tkinter | FastAPI + React |
|---------|---------|-----------------|
| UI Responsiveness | ❌ Freezes | ✅ Always responsive |
| Real-time Updates | ❌ Polling | ✅ WebSocket |
| Multiple Operations | ❌ Sequential | ✅ Concurrent |
| Modern UI | ❌ Basic | ✅ Beautiful |
| Mobile Support | ❌ No | ✅ Yes |
| API Access | ❌ No | ✅ Yes |
| Scalability | ❌ Limited | ✅ Excellent |
| Development | ❌ Slow | ✅ Fast (hot reload) |
| Testing | ❌ Difficult | ✅ Easy |
| Deployment | ❌ Desktop only | ✅ Web + Desktop |

## Resources

- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- TanStack Query: https://tanstack.com/query
- Tailwind CSS: https://tailwindcss.com/
- Vite: https://vitejs.dev/
