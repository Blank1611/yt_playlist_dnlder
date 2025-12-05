# End User Setup Guide

## For Non-Technical Users

This guide helps you set up and use the YouTube Playlist Manager without needing programming knowledge.

## What You Need

### Required Software

1. **Python 3.8 or higher**
   - Download: https://www.python.org/downloads/
   - During installation: ✅ Check "Add Python to PATH"

2. **Node.js 16 or higher**
   - Download: https://nodejs.org/
   - Choose "LTS" (Long Term Support) version
   - Install with default settings

3. **Git** (to download the project)
   - Download: https://git-scm.com/downloads
   - Install with default settings

### Optional (Recommended)

- **Modern web browser** (Chrome, Firefox, Edge)
- **Text editor** (Notepad++, VS Code) for editing config files

## Step-by-Step Setup

### Step 1: Download the Project

**Option A: Using Git (Recommended)**
```bash
# Open Command Prompt or Terminal
git clone https://github.com/YOUR_USERNAME/youtube-playlist-manager.git
cd youtube-playlist-manager
```

**Option B: Download ZIP**
1. Go to GitHub repository
2. Click green "Code" button
3. Click "Download ZIP"
4. Extract to a folder (e.g., `C:\YouTube Manager`)
5. Open Command Prompt in that folder

### Step 2: Set Up Backend

```bash
# Navigate to backend folder
cd yt_serve\backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed fastapi-0.109.0 uvicorn-0.27.0 ...
```

### Step 3: Configure Settings

1. **Copy the example config:**
   ```bash
   copy .env.example .env
   ```

2. **Edit `.env` file** (use Notepad or any text editor):
   ```
   BASE_DOWNLOAD_PATH=E:\\Music\\YouTube
   AUDIO_EXTRACT_MODE=copy
   MAX_CONCURRENT_EXTRACTIONS=4
   BATCH_SIZE=200
   ```

3. **Change `BASE_DOWNLOAD_PATH`** to where you want videos saved
   - Use double backslashes: `E:\\Music\\YouTube`
   - Or forward slashes: `E:/Music/YouTube`

### Step 4: Set Up Frontend

```bash
# Go back to project root
cd ..\..

# Navigate to frontend folder
cd yt_serve\frontend

# Install JavaScript packages (this takes a few minutes)
npm install
```

**Expected output:**
```
added 279 packages in 45s
```

**Note:** This creates the `node_modules` folder (100+ MB). This is normal!

### Step 5: Import Existing Playlists (Optional)

If you have playlists from the old Tkinter app:

```bash
# Go back to project root
cd ..\..

# Run migration
python migrate_playlists.py
```

This imports your playlists from `yt_playlist_gui_config.json`.

## Running the Application

### Every Time You Want to Use It

**You need TWO terminal windows:**

#### Terminal 1: Backend
```bash
cd yt_serve\backend
venv\Scripts\activate
python run.py
```

**You should see:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Keep this window open!**

#### Terminal 2: Frontend
```bash
cd yt_serve\frontend
npm run dev
```

**You should see:**
```
  VITE v5.0.11  ready in 234 ms
  ➜  Local:   http://localhost:5173/
```

**Keep this window open!**

### Open Your Browser

Go to: **http://localhost:5173**

You should see the YouTube Playlist Manager interface!

## Using the Application

### Add a Playlist

1. Copy YouTube playlist URL
   - Example: `https://www.youtube.com/playlist?list=PLxxx...`
2. Paste in "Add Playlist" field
3. Click "Add" button
4. Wait for playlist to appear

### Download Videos

1. Find your playlist in the grid
2. Click "Both" button (downloads + extracts audio)
3. Watch progress bar
4. Files saved to your configured folder

### Other Features

- **Download Only** - Green button (↓)
- **Extract Audio Only** - Purple button (♪)
- **Refresh Stats** - Gray circular arrow button
- **Edit Exclusions** - Click "Edit" next to excluded count
- **Settings** - Gear icon (⚙️) in top right
- **Dark Mode** - Moon/sun icon in top right

## Troubleshooting

### "Python not found"

**Solution:**
1. Reinstall Python
2. ✅ Check "Add Python to PATH"
3. Restart Command Prompt

### "npm not found"

**Solution:**
1. Reinstall Node.js
2. Restart Command Prompt
3. Try: `node --version`

### Backend won't start

**Check:**
- Is virtual environment activated? (should see `(venv)` in prompt)
- Did `pip install` complete successfully?
- Is port 8000 already in use?

**Solution:**
```bash
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <process_id> /F
```

### Frontend won't start

**Check:**
- Did `npm install` complete successfully?
- Is port 5173 already in use?

**Solution:**
```bash
# Delete node_modules and reinstall
rmdir /s /q node_modules
npm install
```

### Can't access http://localhost:5173

**Check:**
- Is frontend running? (check Terminal 2)
- Is backend running? (check Terminal 1)
- Try: http://127.0.0.1:5173

### Downloads not working

**Check:**
- Is download path correct in Settings?
- Does folder exist?
- Do you have write permissions?
- Is yt-dlp up to date?

**Update yt-dlp:**
```bash
pip install --upgrade yt-dlp
```

## Stopping the Application

1. **Close browser tab**
2. **Stop frontend:** Press `Ctrl+C` in Terminal 2
3. **Stop backend:** Press `Ctrl+C` in Terminal 1
4. **Close terminals**

## Updating the Application

When new version is released:

```bash
# Update code
git pull

# Update backend packages
cd yt_serve\backend
venv\Scripts\activate
pip install --upgrade -r requirements.txt

# Update frontend packages
cd ..\frontend
npm install

# Restart both servers
```

## File Locations

### Your Data

- **Downloaded videos:** `{BASE_DOWNLOAD_PATH}/{Playlist Name}/`
- **Audio files:** Same folder as videos
- **Database:** `yt_serve/backend/yt_manager.db`
- **Logs:** `{BASE_DOWNLOAD_PATH}/logs/`

### Configuration

- **Backend settings:** `yt_serve/backend/.env`
- **Frontend settings:** Browser localStorage

## Backup Your Data

**Important files to backup:**
- `yt_serve/backend/yt_manager.db` (your playlists)
- `yt_serve/backend/.env` (your settings)
- Downloaded videos folder

**Don't need to backup:**
- `node_modules/` (can be regenerated)
- `venv/` (can be regenerated)
- Log files (unless you need them)

## Getting Help

### Check Logs

**Backend logs:** Look at Terminal 1 output

**Frontend logs:** 
1. Press F12 in browser
2. Go to "Console" tab
3. Look for errors (red text)

**Job logs:** `{BASE_DOWNLOAD_PATH}/logs/job_{id}.log`

### Common Issues

1. **Port already in use** - Close other applications
2. **Permission denied** - Run as administrator
3. **Module not found** - Reinstall packages
4. **Database locked** - Close other instances

### Documentation

- [GETTING_STARTED.md](yt_serve/GETTING_STARTED.md) - Quick start
- [TROUBLESHOOTING.md](yt_serve/TROUBLESHOOTING.md) - Common problems
- [FRONTEND_COMPLETE.md](yt_serve/FRONTEND_COMPLETE.md) - UI features

## Tips for Best Experience

### Performance

- Close other applications
- Use SSD for downloads
- Stable internet connection
- Don't run multiple jobs simultaneously

### Organization

- Use descriptive playlist names
- Regularly refresh stats
- Clean up old exclusions
- Check logs for errors

### Maintenance

- Update yt-dlp monthly
- Backup database weekly
- Clear old logs periodically
- Check for app updates

## Summary

**Setup (one time):**
1. Install Python, Node.js, Git
2. Download project
3. Install backend packages
4. Install frontend packages
5. Configure settings

**Daily use:**
1. Start backend (Terminal 1)
2. Start frontend (Terminal 2)
3. Open browser
4. Manage playlists
5. Stop servers when done

**That's it!** You're ready to manage your YouTube playlists! 🎉
