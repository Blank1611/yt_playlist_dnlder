# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+** - [Download](https://nodejs.org/)
- **Git** - [Download](https://git-scm.com/)

## Setup

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/youtube-playlist-manager.git
cd youtube-playlist-manager
```

### 2. Backend Setup

```bash
cd yt_serve/backend
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
# Edit .env with your download path
```

### 3. Frontend Setup

```bash
cd ../frontend
npm install
```

### 4. Import Existing Playlists (Optional)

```bash
cd ../..
python migrate_playlists.py
```

## Run

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

**Open Browser:** http://localhost:5173

## Usage

1. **Add Playlist** - Paste YouTube playlist URL
2. **Download** - Click "Both" button
3. **Monitor** - Watch progress bar
4. **Enjoy** - Files saved to configured folder

## Documentation

- **End Users:** [DOCS/end-user-docs/](DOCS/end-user-docs/)
- **Developers:** [DOCS/developer-docs/](DOCS/developer-docs/)

## Need Help?

- [End User Guide](DOCS/end-user-docs/END_USER_GUIDE.md)
- [Troubleshooting](DOCS/end-user-docs/TROUBLESHOOTING.md)
- [Developer Guide](DOCS/developer-docs/DEVELOPER_GUIDE.md)

## Features

✅ Download YouTube playlists  
✅ Extract audio automatically  
✅ Batch downloading (200/day limit)  
✅ Real-time progress tracking  
✅ Dark mode  
✅ Exclusions management  
✅ Settings editor  

Happy downloading! 🎵
