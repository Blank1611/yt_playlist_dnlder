# YouTube Playlist Manager

A modern web-based application for downloading and managing YouTube playlists with automatic audio extraction.

## Overview

This application helps you download entire YouTube playlists, extract audio, and manage your collection efficiently. It features a modern React frontend and a Python FastAPI backend.

### Key Features

- 📥 **Batch Downloads** - Download entire playlists with progress tracking
- 🎵 **Audio Extraction** - Automatic audio extraction from videos
- 🚀 **Real-time Updates** - Live progress bars and status updates
- 🌙 **Dark Mode** - Easy on the eyes
- ⚙️ **Settings Editor** - Configure all options through UI
- 🚫 **Exclusions Management** - Skip specific videos
- 📊 **Smart Sorting** - Prioritizes playlists needing downloads
- 🔄 **Migration Tool** - Import from old Tkinter version

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for a 5-minute setup guide.

## Documentation

### For End Users

Complete guides for using the application:

- **[End User Guide](DOCS/end-user-docs/END_USER_GUIDE.md)** - Complete setup and usage
- **[Getting Started](DOCS/end-user-docs/GETTING_STARTED.md)** - First-time setup
- **[Troubleshooting](DOCS/end-user-docs/TROUBLESHOOTING.md)** - Common issues
- **[Migration Guide](DOCS/end-user-docs/MIGRATION_GUIDE.md)** - Import from Tkinter app

[Browse all end-user docs →](DOCS/end-user-docs/)

### For Developers

Technical documentation for contributors:

- **[Developer Guide](DOCS/developer-docs/DEVELOPER_GUIDE.md)** - Development setup
- **[Architecture](DOCS/developer-docs/COMPLETE.md)** - System design
- **[API Documentation](DOCS/developer-docs/TESTING_GUIDE.md)** - API endpoints
- **[Frontend Guide](DOCS/developer-docs/FRONTEND_COMPLETE.md)** - React app details

[Browse all developer docs →](DOCS/developer-docs/)

## Technology Stack

### Backend
- **Python 3.8+** with FastAPI
- **SQLite** database
- **yt-dlp** for downloads
- **WebSocket** for real-time updates

### Frontend
- **React 18** with TypeScript
- **Vite** for build tooling
- **TanStack Query** for data fetching
- **Tailwind CSS** for styling

## Screenshots

### Main Interface
- Grid view of all playlists
- Real-time progress tracking
- Smart sorting (pending downloads first)
- Color-coded caught-up playlists

### Features
- Settings modal for configuration
- Exclusions editor for managing skipped videos
- Dark mode toggle
- Responsive design

## Installation

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- Git

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/youtube-playlist-manager.git
   cd youtube-playlist-manager
   ```

2. **Set up backend**
   ```bash
   cd yt_serve/backend
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Set up frontend**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Run the application**
   
   Terminal 1 (Backend):
   ```bash
   cd yt_serve/backend
   venv\Scripts\activate
   python run.py
   ```
   
   Terminal 2 (Frontend):
   ```bash
   cd yt_serve/frontend
   npm run dev
   ```

5. **Open browser**
   
   Navigate to http://localhost:5173

## Usage

1. **Add a playlist** - Paste YouTube playlist URL and click "Add"
2. **Download videos** - Click "Both" to download and extract audio
3. **Monitor progress** - Watch real-time progress bars
4. **Manage exclusions** - Click "Edit" to skip specific videos
5. **Configure settings** - Click gear icon to adjust options

## Project Structure

```
youtube-playlist-manager/
├── DOCS/                          # Documentation
│   ├── developer-docs/           # For developers
│   └── end-user-docs/            # For users
├── yt_serve/                     # Web application
│   ├── backend/                  # Python FastAPI backend
│   └── frontend/                 # React TypeScript frontend
├── yt_playlist_audio_tools.py   # Core download logic
├── migrate_playlists.py         # Migration script
├── README.md                     # This file
└── QUICKSTART.md                 # Quick setup guide
```

## Features in Detail

### Download Management
- Batch downloading with configurable limits
- Automatic retry on transient errors
- Error classification (permanent vs temporary)
- Custom archive system

### Audio Extraction
- Multiple modes (copy, MP3, Opus)
- Parallel extraction (configurable workers)
- Automatic fallback on errors

### User Interface
- Modern, responsive design
- Real-time progress tracking
- Dark mode support
- Settings editor
- Exclusions management
- Smart playlist sorting

### Migration
- Import playlists from Tkinter version
- Preserve all metadata
- Safe, non-destructive process

## Contributing

We welcome contributions! Please see:

- [Developer Guide](DOCS/developer-docs/DEVELOPER_GUIDE.md) for setup
- [Architecture docs](DOCS/developer-docs/COMPLETE.md) for design
- GitHub Issues for bug reports and feature requests

## Troubleshooting

Common issues and solutions:

- **Backend won't start** - Check Python version, virtual environment
- **Frontend won't start** - Run `npm install`, check Node version
- **Downloads fail** - Update yt-dlp: `pip install --upgrade yt-dlp`
- **Port conflicts** - Change ports in config files

See [Troubleshooting Guide](DOCS/end-user-docs/TROUBLESHOOTING.md) for more help.

## License

[Your License Here]

## Acknowledgments

- **yt-dlp** - YouTube download library
- **FastAPI** - Modern Python web framework
- **React** - UI framework
- **Tailwind CSS** - Styling framework

## Support

- 📖 [Documentation](DOCS/)
- 🐛 [Report Issues](https://github.com/YOUR_USERNAME/youtube-playlist-manager/issues)
- 💬 [Discussions](https://github.com/YOUR_USERNAME/youtube-playlist-manager/discussions)

---

**Made with ❤️ for YouTube playlist enthusiasts**
