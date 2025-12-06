# Easy Installation Guide for Non-Technical Users

## Choose Your Installation Method

We offer **4 ways** to run the application, from easiest to most advanced:

### 🥇 Method 1: One-Click Launcher (Easiest!)

**Best for:** Windows users who can install Python and Node.js

**Steps:**
1. Install Python: https://www.python.org/downloads/ (check "Add to PATH")
2. Install Node.js: https://nodejs.org/ (use LTS version)
3. Download this project
4. Double-click `LAUNCH_APP.bat`
5. Done! Browser opens automatically

**First run:** Takes 2-3 minutes to set up  
**Next runs:** Instant!

---

### 🥈 Method 2: Portable Package

**Best for:** Users who want a pre-packaged version

**Steps:**
1. Install Python and Node.js (same as above)
2. Download `YouTubePlaylistManager_Portable.zip`
3. Extract anywhere
4. Double-click `LAUNCH_APP.bat`
5. Done!

**Download:** [Get Portable Package](#) (if available)

---

### 🥉 Method 3: Standalone EXE

**Best for:** Users who want a single executable

**Steps:**
1. Install Python and Node.js (same as above)
2. Download `YouTubePlaylistManager.exe`
3. Place in project folder
4. Double-click the EXE
5. Done!

**Download:** [Get EXE](#) (if available)

---

### 🏆 Method 4: Docker (Most User-Friendly!)

**Best for:** Users comfortable with Docker

**Steps:**
1. Install Docker Desktop: https://www.docker.com/products/docker-desktop
2. Download this project
3. Double-click `DOCKER_LAUNCH.bat`
4. Done!

**Advantages:**
- No Python/Node.js needed
- Everything in one container
- Clean and isolated
- Easy to update

---

## Detailed Instructions

### Method 1: One-Click Launcher

#### Prerequisites

**1. Install Python**
- Go to: https://www.python.org/downloads/
- Download latest version (3.8 or higher)
- Run installer
- ✅ **IMPORTANT:** Check "Add Python to PATH"
- Click "Install Now"

**2. Install Node.js**
- Go to: https://nodejs.org/
- Download LTS version (recommended)
- Run installer
- Use default settings
- Click "Next" through all steps

**3. Verify Installation**
- Open Command Prompt
- Type: `python --version`
- Type: `node --version`
- Both should show version numbers

#### Running the App

1. **Download Project**
   - Download ZIP from GitHub
   - Extract to a folder (e.g., `C:\YouTubeManager`)

2. **Launch**
   - Open the folder
   - Double-click `LAUNCH_APP.bat`

3. **First Run**
   - Script checks Python and Node.js
   - Creates virtual environment
   - Installs dependencies (2-3 minutes)
   - Asks you to configure settings
   - Starts servers
   - Opens browser

4. **Configure Settings**
   - Edit `yt_serve\backend\.env`
   - Change `BASE_DOWNLOAD_PATH` to where you want videos
   - Example: `E:\\Music\\YouTube`
   - Save and close

5. **Enjoy!**
   - Browser opens to http://localhost:5173
   - Add playlists and start downloading

#### Next Runs

- Just double-click `LAUNCH_APP.bat`
- Starts instantly (no setup needed)
- Browser opens automatically

---

### Method 4: Docker (Recommended for Simplicity)

#### Prerequisites

**Install Docker Desktop**
- Go to: https://www.docker.com/products/docker-desktop
- Download for Windows
- Run installer
- Restart computer if prompted
- Start Docker Desktop

#### Running the App

1. **Download Project**
   - Same as Method 1

2. **Launch**
   - Double-click `DOCKER_LAUNCH.bat`
   - First time: Downloads and builds (5-10 minutes)
   - Next times: Starts instantly

3. **Access**
   - Browser opens to http://localhost:5173
   - Everything just works!

#### Advantages

- ✅ No Python/Node.js installation
- ✅ No dependency management
- ✅ Clean and isolated
- ✅ Easy updates
- ✅ Works on Windows, Mac, Linux

---

## Comparison

| Method | Setup Time | Prerequisites | Difficulty | Updates |
|--------|------------|---------------|------------|---------|
| One-Click Launcher | 5 min | Python, Node.js | ⭐ Easy | Manual |
| Portable Package | 5 min | Python, Node.js | ⭐ Easy | Manual |
| Standalone EXE | 2 min | Python, Node.js | ⭐ Easy | Manual |
| Docker | 10 min | Docker only | ⭐⭐ Medium | Easy |

## Troubleshooting

### "Python not found"

**Solution:**
1. Reinstall Python
2. ✅ Check "Add Python to PATH"
3. Restart Command Prompt
4. Try again

### "Node not found"

**Solution:**
1. Reinstall Node.js
2. Use default settings
3. Restart Command Prompt
4. Try again

### "Port already in use"

**Solution:**
1. Close other applications
2. Check if app is already running
3. Restart computer
4. Try again

### Docker won't start

**Solution:**
1. Make sure Docker Desktop is running
2. Check system requirements
3. Restart Docker Desktop
4. Try again

## Getting Help

- 📖 [Full Documentation](../DOCS/)
- 🐛 [Report Issues](https://github.com/YOUR_USERNAME/youtube-playlist-manager/issues)
- 💬 [Ask Questions](https://github.com/YOUR_USERNAME/youtube-playlist-manager/discussions)

---

**Choose the method that works best for you and enjoy!** 🎵
