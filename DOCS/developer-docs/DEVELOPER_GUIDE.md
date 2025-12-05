# Developer Setup Guide

## For Developers & Contributors

This guide is for developers who want to contribute, modify, or understand the codebase.

## Prerequisites

### Required

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Git** for version control
- **Code editor** (VS Code recommended)

### Recommended

- **Python virtual environment** knowledge
- **FastAPI** experience
- **React** + **TypeScript** experience
- **REST API** understanding
- **Git workflow** knowledge

## Project Structure

```
youtube-playlist-manager/
├── yt_serve/                      # Web application
│   ├── backend/                   # Python FastAPI backend
│   │   ├── app/
│   │   │   ├── api/              # API endpoints
│   │   │   │   ├── playlists.py  # Playlist CRUD
│   │   │   │   ├── downloads.py  # Job management
│   │   │   │   ├── config.py     # Configuration
│   │   │   │   └── websocket.py  # Real-time updates
│   │   │   ├── core/
│   │   │   │   └── config.py     # Settings management
│   │   │   ├── models/
│   │   │   │   └── database.py   # SQLAlchemy models
│   │   │   ├── services/
│   │   │   │   ├── ytdlp_service.py    # Download logic
│   │   │   │   └── job_manager.py      # Background jobs
│   │   │   └── main.py           # FastAPI app
│   │   ├── requirements.txt      # Python dependencies
│   │   ├── run.py               # Entry point
│   │   └── .env.example         # Config template
│   │
│   └── frontend/                 # React TypeScript frontend
│       ├── src/
│       │   ├── App.tsx          # Main component
│       │   ├── api.ts           # API client
│       │   ├── types.ts         # TypeScript types
│       │   ├── main.tsx         # Entry point
│       │   └── index.css        # Global styles
│       ├── package.json         # Node dependencies
│       ├── tsconfig.json        # TypeScript config
│       ├── vite.config.ts       # Vite config
│       └── tailwind.config.js   # Tailwind config
│
├── yt_playlist_audio_tools.py   # Core download logic
├── yt_playlist_manager_gui_final.py  # Tkinter app (legacy)
├── migrate_playlists.py         # Migration script
├── .gitignore                   # Git exclusions
└── README.md                    # Project overview
```

## Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/youtube-playlist-manager.git
cd youtube-playlist-manager
```

### 2. Backend Setup

```bash
cd yt_serve/backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your settings
# BASE_DOWNLOAD_PATH, etc.
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# This creates node_modules/ (~100MB)
# Takes 1-2 minutes
```

### 4. Run Development Servers

**Terminal 1 - Backend:**
```bash
cd yt_serve/backend
venv\Scripts\activate
python run.py
```

**Terminal 2 - Frontend:**
```bash
cd yt_serve/frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Development Workflow

### Making Changes

#### Backend Changes

1. **Edit Python files** in `yt_serve/backend/app/`
2. **Backend auto-reloads** (uvicorn --reload)
3. **Test API** at http://localhost:8000/docs
4. **Check logs** in terminal

#### Frontend Changes

1. **Edit TypeScript files** in `yt_serve/frontend/src/`
2. **Frontend auto-reloads** (Vite HMR)
3. **Test UI** at http://localhost:5173
4. **Check console** (F12 in browser)

### Testing

#### Backend Testing

```bash
# Manual testing via API docs
http://localhost:8000/docs

# Or use curl
curl http://localhost:8000/api/playlists

# Check diagnostics
python -m pylint app/
```

#### Frontend Testing

```bash
# Type checking
npm run build

# Linting
npm run lint

# Browser console (F12)
# Check for errors
```

### Code Style

#### Python (Backend)

- **PEP 8** style guide
- **Type hints** where possible
- **Docstrings** for functions
- **async/await** for I/O operations

```python
async def download_playlist(
    self,
    url: str,
    excluded_ids: Set[str],
    progress_callback: Optional[Callable] = None
) -> Set[str]:
    """
    Download playlist with progress tracking
    
    Args:
        url: Playlist URL
        excluded_ids: Video IDs to skip
        progress_callback: Progress update function
    
    Returns:
        Set of failed video IDs
    """
    pass
```

#### TypeScript (Frontend)

- **ESLint** rules
- **TypeScript strict mode**
- **Functional components**
- **Hooks** for state management

```typescript
interface Playlist {
  id: number
  url: string
  title: string
  local_count: number
  playlist_count: number
  excluded_ids: string[]
}

function PlaylistCard({ playlist }: { playlist: Playlist }) {
  const [isLoading, setIsLoading] = useState(false)
  // ...
}
```

## Architecture

### Backend Architecture

```
FastAPI App
├── API Routes (REST endpoints)
├── WebSocket (Real-time updates)
├── Job Manager (Background tasks)
├── Download Service (yt-dlp wrapper)
├── Database (SQLite + SQLAlchemy)
└── File System (Logs)
```

**Key Concepts:**
- **Async/await** for non-blocking I/O
- **Background tasks** for downloads
- **WebSocket** for real-time updates
- **Dependency injection** for services

### Frontend Architecture

```
React App
├── Components (UI elements)
├── TanStack Query (Data fetching)
├── API Client (Axios)
├── State Management (React hooks)
└── Styling (Tailwind CSS)
```

**Key Concepts:**
- **Component-based** architecture
- **Query caching** with TanStack Query
- **Optimistic updates** for better UX
- **Responsive design** with Tailwind

## API Endpoints

### Playlists

```
GET    /api/playlists           # List all
POST   /api/playlists           # Create
GET    /api/playlists/{id}      # Get one
PUT    /api/playlists/{id}      # Update
DELETE /api/playlists/{id}      # Delete
POST   /api/playlists/{id}/refresh  # Refresh stats
```

### Jobs

```
GET    /api/downloads/jobs      # List all
POST   /api/downloads/jobs      # Create
GET    /api/downloads/jobs/{id} # Get one
POST   /api/downloads/jobs/{id}/cancel  # Cancel
GET    /api/downloads/jobs/{id}/logs    # Get logs
```

### Config

```
GET    /api/config              # Get settings
PUT    /api/config              # Update settings
```

### WebSocket

```
WS     /ws/logs/{job_id}        # Real-time logs
WS     /ws/progress/{job_id}    # Real-time progress
```

## Database Schema

### Playlists Table

```sql
CREATE TABLE playlists (
    id INTEGER PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    local_count INTEGER DEFAULT 0,
    playlist_count INTEGER DEFAULT 0,
    unavailable_count INTEGER DEFAULT 0,
    last_download DATETIME,
    last_extract DATETIME,
    excluded_ids JSON,
    created_at DATETIME,
    updated_at DATETIME
);
```

### Jobs Table

```sql
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY,
    playlist_id INTEGER NOT NULL,
    job_type TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    progress REAL DEFAULT 0.0,
    total_items INTEGER DEFAULT 0,
    completed_items INTEGER DEFAULT 0,
    failed_items INTEGER DEFAULT 0,
    error TEXT,
    created_at DATETIME,
    started_at DATETIME,
    completed_at DATETIME
);
```

## Adding New Features

### Backend Feature

1. **Create API endpoint** in `app/api/`
2. **Add service logic** in `app/services/`
3. **Update models** if needed in `app/models/`
4. **Test via** http://localhost:8000/docs

**Example:**
```python
# app/api/playlists.py
@router.post("/playlists/{id}/archive")
async def archive_playlist(id: int, db: Session = Depends(get_db)):
    """Archive a playlist"""
    playlist = db.query(Playlist).filter(Playlist.id == id).first()
    if not playlist:
        raise HTTPException(status_code=404)
    
    playlist.archived = True
    db.commit()
    return playlist
```

### Frontend Feature

1. **Add API call** in `src/api.ts`
2. **Create component** or update existing
3. **Add state management** with hooks
4. **Style with** Tailwind CSS

**Example:**
```typescript
// src/api.ts
export const playlistsApi = {
  archive: (id: number) => api.post(`/playlists/${id}/archive`),
}

// src/App.tsx
const archivePlaylist = useMutation({
  mutationFn: (id: number) => playlistsApi.archive(id),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['playlists'] })
  },
})
```

## Debugging

### Backend Debugging

**Print statements:**
```python
print(f"Debug: {variable}")
```

**Logging:**
```python
import logging
logging.info("Info message")
logging.error("Error message")
```

**Breakpoints:**
```python
import pdb; pdb.set_trace()
```

### Frontend Debugging

**Console logs:**
```typescript
console.log('Debug:', variable)
console.error('Error:', error)
```

**React DevTools:**
- Install browser extension
- Inspect component state
- View props and hooks

**Network tab:**
- F12 → Network
- See API requests
- Check responses

## Git Workflow

### Branching

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes
git add .
git commit -m "Add new feature"

# Push to GitHub
git push origin feature/new-feature

# Create Pull Request on GitHub
```

### Commit Messages

**Format:**
```
<type>: <description>

[optional body]
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting
- `refactor:` Code restructure
- `test:` Tests
- `chore:` Maintenance

**Examples:**
```
feat: Add exclusions editor modal
fix: Cancel button now properly stops downloads
docs: Update developer guide
style: Format code with prettier
refactor: Extract settings modal to component
```

## Building for Production

### Backend

```bash
cd yt_serve/backend

# Install production dependencies
pip install -r requirements.txt

# Run with production server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd yt_serve/frontend

# Build for production
npm run build

# Output in dist/ folder
# Serve with any static file server
npx serve dist
```

## Deployment

### Option 1: Local Server

- Run backend with uvicorn
- Serve frontend dist/ with nginx
- Use systemd for auto-start

### Option 2: Docker

```dockerfile
# Backend Dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

### Option 3: Cloud

- **Backend:** Heroku, Railway, Render
- **Frontend:** Vercel, Netlify, GitHub Pages
- **Database:** PostgreSQL (instead of SQLite)

## Contributing

### Before Submitting PR

1. ✅ Code follows style guide
2. ✅ All tests pass
3. ✅ No console errors
4. ✅ Documentation updated
5. ✅ Commit messages clear

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation

## Testing
How to test the changes

## Screenshots
If UI changes
```

## Resources

### Documentation

- **FastAPI:** https://fastapi.tiangolo.com/
- **React:** https://react.dev/
- **TanStack Query:** https://tanstack.com/query/
- **Tailwind CSS:** https://tailwindcss.com/
- **yt-dlp:** https://github.com/yt-dlp/yt-dlp

### Tools

- **VS Code:** https://code.visualstudio.com/
- **Postman:** https://www.postman.com/
- **React DevTools:** Browser extension
- **SQLite Browser:** https://sqlitebrowser.org/

## Common Tasks

### Add New API Endpoint

1. Define route in `app/api/`
2. Add Pydantic models
3. Implement logic
4. Test in /docs
5. Update frontend API client

### Add New UI Component

1. Create component in `src/`
2. Add TypeScript types
3. Style with Tailwind
4. Connect to API
5. Test in browser

### Update Dependencies

```bash
# Backend
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt

# Frontend
npm update
npm audit fix
```

### Database Migration

```bash
# If schema changes
# 1. Update models in database.py
# 2. Delete old database
rm yt_manager.db
# 3. Restart backend (creates new schema)
python run.py
```

## Summary

**Setup:**
1. Clone repo
2. Install backend deps
3. Install frontend deps
4. Configure .env
5. Run both servers

**Development:**
1. Make changes
2. Test locally
3. Commit with clear message
4. Push to GitHub
5. Create PR

**Best Practices:**
- Write clean code
- Add comments
- Test thoroughly
- Update docs
- Follow conventions

Happy coding! 🚀
