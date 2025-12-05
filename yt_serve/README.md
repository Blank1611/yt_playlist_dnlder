# YouTube Playlist Manager - Web Version

This is the web-based version of the YouTube Playlist Manager, featuring a modern React frontend and Python FastAPI backend.

## Quick Links

- **Main README:** [../README.md](../README.md)
- **Quick Start:** [../QUICKSTART.md](../QUICKSTART.md)
- **Documentation:** [../DOCS/](../DOCS/)

## Structure

```
yt_serve/
├── backend/          # Python FastAPI backend
│   ├── app/         # Application code
│   ├── run.py       # Entry point
│   └── .env         # Configuration
└── frontend/        # React TypeScript frontend
    ├── src/         # Source code
    └── package.json # Dependencies
```

## Running the Application

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python run.py
```

Backend runs on: http://localhost:8000

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on: http://localhost:5173

## Documentation

All documentation has been organized in the main DOCS folder:

### For End Users
- [End User Guide](../DOCS/end-user-docs/END_USER_GUIDE.md)
- [Getting Started](../DOCS/end-user-docs/GETTING_STARTED.md)
- [Troubleshooting](../DOCS/end-user-docs/TROUBLESHOOTING.md)
- [Migration Guide](../DOCS/end-user-docs/MIGRATION_GUIDE.md)

### For Developers
- [Developer Guide](../DOCS/developer-docs/DEVELOPER_GUIDE.md)
- [Backend Architecture](../DOCS/developer-docs/COMPLETE.md)
- [Frontend Guide](../DOCS/developer-docs/FRONTEND_COMPLETE.md)
- [API Testing](../DOCS/developer-docs/TESTING_GUIDE.md)

## Features

✅ **Backend (FastAPI)**
- RESTful API endpoints
- WebSocket for real-time updates
- Background job processing
- SQLite database
- File system logging

✅ **Frontend (React)**
- Modern, responsive UI
- Real-time progress tracking
- Dark mode
- Settings editor
- Exclusions management
- TanStack Query for data fetching

## API Documentation

Once the backend is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Development

Both backend and frontend support hot-reload during development:

- **Backend:** Uvicorn auto-reloads on file changes
- **Frontend:** Vite HMR (Hot Module Replacement)

See [Developer Guide](../DOCS/developer-docs/DEVELOPER_GUIDE.md) for detailed development instructions.

## Migration from Tkinter

To import playlists from the old Tkinter version:

```bash
cd ..
python migrate_playlists.py
```

See [Migration Guide](../DOCS/end-user-docs/MIGRATION_GUIDE.md) for details.

---

For complete documentation, see [../DOCS/](../DOCS/)
