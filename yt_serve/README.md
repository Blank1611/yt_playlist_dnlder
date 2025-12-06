# YouTube Playlist Manager - Web Version

A modern web-based YouTube playlist manager with React frontend and FastAPI backend.

## Quick Start

### Prerequisites

- Python 3.8+ (you have 3.14.0 ✓)
- Node.js 16+

### Installation

**Option 1: One-Click Launcher (Easiest)**
```bash
# Just double-click
LAUNCH_APP.bat
```

**Option 2: Manual**
```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

**Option 3: Docker**
```bash
docker-compose up
```

### Access

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Features

✅ Modern React UI with TypeScript  
✅ FastAPI backend with async support  
✅ Real-time progress tracking  
✅ Dark mode  
✅ Settings editor  
✅ Exclusions management  
✅ Batch downloading  
✅ Parallel audio extraction  

## Documentation

📚 **[Complete Documentation](DOCS/)** - All guides and references

### Quick Links
- **[DOCS/QUICKSTART.md](DOCS/QUICKSTART.md)** - Get started in 5 minutes
- **[DOCS/FIRST_RUN_SETUP.md](DOCS/FIRST_RUN_SETUP.md)** - First-run setup wizard
- **[DOCS/END_USER_GUIDE.md](DOCS/END_USER_GUIDE.md)** - Complete user guide
- **[DOCS/DEVELOPER_GUIDE.md](DOCS/DEVELOPER_GUIDE.md)** - Developer documentation
- **[DOCS/TROUBLESHOOTING.md](DOCS/TROUBLESHOOTING.md)** - Common issues & solutions

See **[DOCS/README.md](DOCS/README.md)** for complete documentation index.

## Project Structure

```
yt_serve/
├── backend/              # Python FastAPI backend
│   ├── app/             # Application code
│   ├── run.py           # Entry point
│   └── requirements.txt # Dependencies
├── frontend/            # React TypeScript frontend
│   ├── src/            # Source code
│   └── package.json    # Dependencies
├── DOCS/               # Documentation
├── LAUNCH_APP.bat      # One-click launcher
└── README.md           # This file
```

## Building Installer

```bash
# Install Inno Setup first
# https://jrsoftware.org/isdl.php

# Build installer
python build_installer.py
```

## Independent Project

This project is completely independent and includes:
- ✅ Own copy of `yt_playlist_audio_tools.py`
- ✅ All documentation
- ✅ Build scripts
- ✅ Launcher scripts
- ✅ Docker configuration

Can be distributed separately from the Tkinter version!

## License

[Your License]
