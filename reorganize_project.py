"""
Reorganize project structure:
- Move yt_serve related files into yt_serve/
- Keep only Tkinter version files in root
- Make yt_serve completely independent
"""
import shutil
from pathlib import Path

def reorganize():
    print("="*60)
    print("Reorganizing Project Structure")
    print("="*60)
    print()
    
    root = Path(".")
    yt_serve = root / "yt_serve"
    
    # Files to move into yt_serve/
    files_to_move = [
        # Launcher and build scripts
        "LAUNCH_APP.bat",
        "start_servers.bat",
        "build_exe.py",
        "build_installer.py",
        "create_portable_package.py",
        "launcher.py",
        "setup_dependencies.bat",
        "organize_docs.py",
        "verify_migration.py",
        "migrate_playlists.py",
        
        # Docker files
        "Dockerfile",
        "docker-compose.yml",
        "docker-start.sh",
        "DOCKER_LAUNCH.bat",
        
        # Installer files
        "installer.iss",
        "INSTALL_INFO.txt",
        
        # Documentation summaries
        "END_USER_SOLUTIONS.md",
        "COMPLETE_INSTALLER_SOLUTION.md",
        "DOCS_ORGANIZATION.md",
        "END_USER_GUIDE.md",
        "DEVELOPER_GUIDE.md",
    ]
    
    # Move files
    print("Moving yt_serve related files...")
    moved = 0
    for file in files_to_move:
        src = root / file
        if src.exists():
            dest = yt_serve / file
            try:
                shutil.move(str(src), str(dest))
                print(f"  ✓ {file} -> yt_serve/")
                moved += 1
            except Exception as e:
                print(f"  ✗ {file}: {e}")
    
    # Check if backend core module exists (don't overwrite if already customized)
    print("\nChecking core download module in backend...")
    src = root / "yt_playlist_audio_tools.py"
    dest = yt_serve / "backend" / "app" / "core" / "yt_playlist_audio_tools.py"
    if dest.exists():
        print(f"  ✓ yt_playlist_audio_tools.py already exists in backend (keeping customized version)")
    elif src.exists():
        shutil.copy2(str(src), str(dest))
        print(f"  ✓ yt_playlist_audio_tools.py -> yt_serve/backend/app/core/")
    
    # Update imports in yt_serve/backend
    print("\nUpdating imports in backend...")
    ytdlp_service = yt_serve / "backend" / "app" / "services" / "ytdlp_service.py"
    if ytdlp_service.exists():
        content = ytdlp_service.read_text(encoding='utf-8')
        # Update import path to use relative import
        if "import yt_playlist_audio_tools" in content:
            content = content.replace(
                "import yt_playlist_audio_tools",
                "from app.core import yt_playlist_audio_tools"
            )
            ytdlp_service.write_text(content, encoding='utf-8')
            print("  ✓ Updated ytdlp_service.py imports")
    
    # Create yt_serve README
    print("\nCreating yt_serve README...")
    readme_content = """# YouTube Playlist Manager - Web Version

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
venv\\Scripts\\activate
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

- **[QUICKSTART.md](QUICKSTART.md)** - Quick setup guide
- **[DOCS/](DOCS/)** - Complete documentation
- **[README.md](README.md)** - Main project overview

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
"""
    
    (yt_serve / "README.md").write_text(readme_content, encoding='utf-8')
    print("  ✓ Created yt_serve/README.md")
    
    # Create root README pointing to both versions
    print("\nUpdating root README...")
    root_readme = """# YouTube Playlist Manager

Download and manage YouTube playlists with automatic audio extraction.

## Two Versions Available

### 1. 🖥️ Tkinter Desktop App (Classic)

**Location:** This directory  
**Files:** `yt_playlist_manager_gui_final.py`

**Run:**
```bash
python yt_playlist_manager_gui_final.py
```

**Features:**
- Classic desktop GUI
- Proven and stable
- Simple interface
- All core features

### 2. 🌐 Web Version (Modern)

**Location:** `yt_serve/` directory  
**Tech:** React + FastAPI

**Run:**
```bash
cd yt_serve
# See yt_serve/README.md for details
```

**Features:**
- Modern web interface
- Real-time updates
- Dark mode
- Better performance
- Professional UI

## Quick Start

### Tkinter Version
```bash
python yt_playlist_manager_gui_final.py
```

### Web Version
```bash
cd yt_serve
LAUNCH_APP.bat  # or see yt_serve/README.md
```

## Documentation

- **Tkinter Version:** See markdown files in this directory
- **Web Version:** See `yt_serve/DOCS/`

## Choose Your Version

| Feature | Tkinter | Web |
|---------|---------|-----|
| Interface | Desktop GUI | Web Browser |
| Setup | Simple | Moderate |
| Performance | Good | Excellent |
| UI | Classic | Modern |
| Real-time | No | Yes |
| Mobile | No | Yes |

Both versions use the same core download logic and are fully compatible!

## License

[Your License]
"""
    
    (root / "README.md").write_text(root_readme, encoding='utf-8')
    print("  ✓ Updated root README.md")
    
    print()
    print("="*60)
    print("Reorganization Complete!")
    print("="*60)
    print()
    print(f"Moved {moved} files to yt_serve/")
    print()
    print("Structure:")
    print("  Root/")
    print("    ├── yt_playlist_manager_gui_final.py  (Tkinter)")
    print("    ├── yt_playlist_audio_tools.py        (Core - shared)")
    print("    ├── Tkinter docs and scripts")
    print("    └── yt_serve/                         (Web version)")
    print("        ├── backend/")
    print("        │   └── app/")
    print("        │       └── core/")
    print("        │           └── yt_playlist_audio_tools.py  (Copy)")
    print("        ├── frontend/")
    print("        ├── DOCS/")
    print("        ├── LAUNCH_APP.bat")
    print("        └── All web-related files")
    print()
    print("yt_serve is now completely independent!")
    print()

if __name__ == '__main__':
    reorganize()
