# Getting Started - Complete Guide

## 🚀 Quick Start (5 Minutes)

### Step 1: Backend Setup (2 minutes)

```bash
cd yt_serve/backend

# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies (first time only)
pip install -r requirements.txt

# Start backend
python run.py
```

✅ Backend running on: **http://localhost:8000**

### Step 2: Frontend Setup (2 minutes)

```bash
cd yt_serve/frontend

# Install dependencies (first time only)
npm install

# Start frontend
npm run dev
```

✅ Frontend running on: **http://localhost:5173**

### Step 3: Open Browser (1 minute)

Navigate to: **http://localhost:5173**

You should see your 19 migrated playlists! 🎉

## 📋 What You Have

### ✅ Backend (Python + FastAPI)
- 19 playlists migrated from Tkinter app
- All metadata preserved (counts, exclusions, timestamps)
- RESTful API ready
- WebSocket support for real-time updates
- Job management system
- File system logging

### ✅ Frontend (React + TypeScript)
- Modern, responsive UI
- Real-time progress tracking
- Playlist management
- Job operations (download/extract/both)
- Auto-polling for updates

### ✅ Migration Complete
- All playlists imported
- Configuration preserved
- Compatible with existing files
- Both apps can coexist

## 🎯 Common Tasks

### Add a New Playlist

1. Copy YouTube playlist URL
2. Paste in "Add Playlist" field
3. Click "Add" button
4. Playlist appears with stats

### Download Videos

1. Find playlist in grid
2. Click "Both" button (download + extract audio)
3. Watch progress bar
4. Files saved to configured directory

### Monitor Progress

- Progress bar shows completion %
- Item count shows current/total
- Cancel button available anytime
- Auto-updates every 2 seconds

## 📁 File Locations

### Backend
```
yt_serve/backend/
├── yt_manager.db          # SQLite database (19 playlists)
├── .env                   # Configuration
├── run.py                 # Start script
└── app/                   # Application code
```

### Frontend
```
yt_serve/frontend/
├── src/                   # Source code
├── package.json           # Dependencies
└── vite.config.ts         # Configuration
```

### Downloads
```
E:\2tbhdd\songs\syst\New folder\youtube\
├── Awesome/               # Downloaded videos
├── Hindi/
├── Turk/
└── logs/
    ├── Awesome.log        # Old logs (Tkinter)
    └── job_1.log          # New logs (Web backend)
```

## 🔧 Configuration

### Backend (.env)
```bash
BASE_DOWNLOAD_PATH=E:\\2tbhdd\\songs\\syst\\New folder\\youtube
AUDIO_EXTRACT_MODE=copy
MAX_CONCURRENT_EXTRACTIONS=4
BATCH_SIZE=200
```

### Frontend (vite.config.ts)
```typescript
server: {
  port: 5173,
  proxy: {
    '/api': 'http://localhost:8000',
  },
}
```

## 📚 Documentation

### Quick References
- **[QUICKSTART.md](QUICKSTART.md)** - API usage examples
- **[FRONTEND_COMPLETE.md](FRONTEND_COMPLETE.md)** - Frontend details
- **[COMPLETE.md](COMPLETE.md)** - Backend architecture

### Detailed Guides
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Migration process
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - API testing
- **[LOGGING_ARCHITECTURE.md](LOGGING_ARCHITECTURE.md)** - Log system

### Technical Docs
- **[IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)** - Implementation details
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Setup instructions

## 🎨 Features

### Playlist Management
- ✅ View all playlists
- ✅ Add new playlists
- ✅ Delete playlists
- ✅ Refresh stats
- ✅ View counts (local/total/unavailable)
- ✅ See excluded videos

### Download Operations
- ✅ Download videos
- ✅ Extract audio
- ✅ Both (download + extract)
- ✅ Batch downloading (200/day limit)
- ✅ Error handling
- ✅ Automatic retries

### Job Management
- ✅ Start jobs
- ✅ Cancel jobs
- ✅ Monitor progress
- ✅ View logs
- ✅ Multiple concurrent jobs

### Advanced Features
- ✅ Custom archive system
- ✅ Error classification
- ✅ Parallel audio extraction
- ✅ Old format auto-rename
- ✅ Smart caching
- ✅ Exclusions management

## 🔍 Troubleshooting

### Backend won't start?

**Check Python version:**
```bash
python --version  # Should be 3.8+
```

**Check dependencies:**
```bash
pip install -r requirements.txt
```

**Check port:**
```bash
netstat -ano | findstr :8000
```

### Frontend won't start?

**Check Node version:**
```bash
node --version  # Should be 16+
```

**Reinstall dependencies:**
```bash
rm -rf node_modules package-lock.json
npm install
```

### No playlists showing?

**Verify migration:**
```bash
python verify_migration.py
```

**Re-run migration:**
```bash
python migrate_playlists.py
```

**Restart backend:**
```bash
# Stop backend (Ctrl+C)
python yt_serve/backend/run.py
```

### API not connecting?

**Check backend is running:**
```bash
curl http://localhost:8000/api/playlists
```

**Check proxy configuration:**
- Frontend should proxy `/api` to backend
- Configured in `vite.config.ts`

## 🎓 Learning Resources

### API Documentation
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Code Examples
- See `TESTING_GUIDE.md` for cURL examples
- See `QUICKSTART.md` for common tasks
- See frontend `src/api.ts` for TypeScript examples

## 🚦 Next Steps

### Immediate
1. ✅ Start backend
2. ✅ Start frontend
3. ✅ Test with one playlist
4. ✅ Monitor progress
5. ✅ Check logs

### Short Term
- [ ] Download a few playlists
- [ ] Test audio extraction
- [ ] Try canceling a job
- [ ] Refresh playlist stats
- [ ] Add a new playlist

### Long Term
- [ ] Customize UI colors/layout
- [ ] Add more features (logs viewer, settings)
- [ ] Deploy to production
- [ ] Build mobile app (optional)

## 💡 Tips

### Performance
- Backend handles 1 download + multiple extractions in parallel
- Frontend auto-polls every 2 seconds
- Batch size limits to 200 videos/day (YouTube bot detection)

### Best Practices
- Let jobs complete before starting new ones on same playlist
- Check logs if downloads fail
- Refresh stats periodically
- Keep excluded IDs list updated

### Keyboard Shortcuts
- `Ctrl+C` - Stop backend/frontend
- `Ctrl+Shift+R` - Hard refresh browser
- `F12` - Open browser DevTools

## 🎉 You're Ready!

Everything is set up and ready to use:
- ✅ Backend configured
- ✅ Frontend built
- ✅ Playlists migrated
- ✅ Documentation complete

**Start both servers and enjoy your modern YouTube Playlist Manager!**

---

**Questions?** Check the documentation or test the API at http://localhost:8000/docs
