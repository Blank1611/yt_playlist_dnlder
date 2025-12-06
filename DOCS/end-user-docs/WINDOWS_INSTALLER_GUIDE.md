# Windows Installer Guide

## The Ultimate Easy Installation

This is the **easiest way** to install YouTube Playlist Manager on Windows. Everything is bundled - no prerequisites needed!

## What's Included

The Windows installer includes:

✅ **Portable Python 3.11** - No separate installation  
✅ **Portable Node.js 18** - No separate installation  
✅ **All dependencies** - Installed automatically  
✅ **Desktop shortcut** - Optional  
✅ **Start Menu entry** - Easy access  
✅ **Uninstaller** - Clean removal  

## Installation Steps

### 1. Download Installer

Download `YouTubePlaylistManager_Setup.exe` from:
- GitHub Releases
- Project website
- Direct link

**File size:** ~150 MB (includes everything)

### 2. Run Installer

Double-click `YouTubePlaylistManager_Setup.exe`

**Windows SmartScreen:**
- If you see "Windows protected your PC"
- Click "More info"
- Click "Run anyway"

### 3. Installation Wizard

**Welcome Screen:**
- Click "Next"

**License Agreement:**
- Read and accept
- Click "Next"

**Installation Information:**
- Read what will be installed
- Click "Next"

**Choose Location:**
- Default: `C:\Program Files\YouTube Playlist Manager`
- Or click "Browse" to choose different location
- Click "Next"

**Select Tasks:**
- ☑ Create desktop shortcut (optional)
- ☑ Create Quick Launch icon (optional)
- Click "Next"

**Ready to Install:**
- Review settings
- Click "Install"

### 4. Installation Progress

**Installing files...**
- Copying application files
- Extracting Python runtime
- Extracting Node.js runtime
- Takes ~1 minute

**Setting up dependencies...**
- Creating virtual environment
- Installing Python packages
- Installing Node packages
- Takes ~2-3 minutes

**Total time:** 3-4 minutes

### 5. Completion

**Installation Complete!**
- ☑ Launch YouTube Playlist Manager
- Click "Finish"

**App launches automatically!**
- Browser opens to http://localhost:5173
- Ready to use!

## First Run

### Initial Configuration

1. **Settings Icon** (⚙️) in top right
2. **Configure Download Path**
   - Click "Browse" or type path
   - Example: `E:\Music\YouTube`
3. **Save Settings**

### Add Your First Playlist

1. Copy YouTube playlist URL
2. Paste in "Add Playlist" field
3. Click "Add"
4. Click "Both" to download

Done! Videos downloading!

## Features

### Desktop Shortcut

If you selected desktop shortcut:
- Double-click icon on desktop
- App launches immediately

### Start Menu

Find in Start Menu:
- "YouTube Playlist Manager"
- Click to launch

### Uninstaller

Also in Start Menu:
- "Uninstall YouTube Playlist Manager"
- Click to remove

## System Requirements

**Minimum:**
- Windows 10 (64-bit)
- 4 GB RAM
- 500 MB disk space
- Internet connection

**Recommended:**
- Windows 11 (64-bit)
- 8 GB RAM
- 1 GB disk space
- Fast internet

## Installation Locations

**Application:**
```
C:\Program Files\YouTube Playlist Manager\
├── YouTubePlaylistManager.exe
├── portable\
│   ├── python\
│   └── nodejs\
├── yt_serve\
├── DOCS\
└── ...
```

**User Data:**
```
{Installation}\yt_serve\backend\
├── yt_manager.db (database)
├── .env (configuration)
└── logs\
```

**Downloads:**
```
{Your chosen path}\
├── Playlist 1\
├── Playlist 2\
└── ...
```

## Advantages

### vs Manual Installation

| Aspect | Manual | Installer |
|--------|--------|-----------|
| Python install | ❌ Manual | ✅ Automatic |
| Node.js install | ❌ Manual | ✅ Automatic |
| Dependencies | ❌ Manual | ✅ Automatic |
| Configuration | ❌ Manual | ✅ Guided |
| Shortcuts | ❌ Manual | ✅ Automatic |
| Uninstall | ❌ Manual | ✅ One-click |
| Time | 15-20 min | 3-4 min |

### vs Portable Package

| Aspect | Portable | Installer |
|--------|----------|-----------|
| Prerequisites | Python, Node.js | None |
| Installation | Extract ZIP | Wizard |
| Shortcuts | Manual | Automatic |
| Uninstall | Delete folder | Clean removal |
| Updates | Manual | Easy |

## Troubleshooting

### "Windows protected your PC"

**Cause:** Unsigned executable

**Solution:**
1. Click "More info"
2. Click "Run anyway"
3. Installation continues

### "Installation failed"

**Cause:** Insufficient permissions

**Solution:**
1. Right-click installer
2. "Run as administrator"
3. Try again

### "Not enough disk space"

**Cause:** Less than 500 MB free

**Solution:**
1. Free up disk space
2. Or choose different location
3. Try again

### App won't launch

**Cause:** Antivirus blocking

**Solution:**
1. Add to antivirus exceptions
2. Or temporarily disable
3. Launch again

## Updating

### When Update Available

1. Download new installer
2. Run installer
3. Choose same location
4. Installer updates files
5. Done!

**Your data is preserved:**
- Database
- Configuration
- Downloaded files

## Uninstalling

### Method 1: Settings

1. Windows Settings
2. Apps > Installed apps
3. Find "YouTube Playlist Manager"
4. Click "..." > Uninstall
5. Confirm

### Method 2: Start Menu

1. Start Menu
2. Find "YouTube Playlist Manager"
3. Right-click
4. "Uninstall"
5. Confirm

### Method 3: Control Panel

1. Control Panel
2. Programs > Uninstall a program
3. Find "YouTube Playlist Manager"
4. Click "Uninstall"
5. Confirm

### What Gets Removed

**Removed:**
- Application files
- Python runtime
- Node.js runtime
- Dependencies
- Shortcuts

**Kept (optional):**
- Downloaded videos
- Database
- Configuration
- Logs

**Clean uninstall option:**
- Check "Remove all data"
- Everything deleted

## Building the Installer

### For Developers

To create the installer:

```bash
# Install requirements
pip install pyinstaller

# Download Inno Setup
# https://jrsoftware.org/isdl.php

# Build installer
python build_installer.py
```

**Output:**
```
installer_output/YouTubePlaylistManager_Setup.exe
```

**What it does:**
1. Downloads portable Python
2. Downloads portable Node.js
3. Builds launcher EXE
4. Creates Inno Setup installer
5. Bundles everything

**Time:** 10-15 minutes

## Distribution

### Sharing the Installer

**Upload to:**
- GitHub Releases
- Your website
- File sharing service

**File info:**
- Name: `YouTubePlaylistManager_Setup.exe`
- Size: ~150 MB
- Type: Windows Installer

**Users download and run - that's it!**

## Comparison

### All Installation Methods

| Method | Prerequisites | Time | Difficulty | Best For |
|--------|--------------|------|------------|----------|
| **Windows Installer** | **None** | **4 min** | **⭐ Easiest** | **Everyone** |
| One-Click Launcher | Python, Node.js | 5 min | ⭐⭐ Easy | Windows users |
| Portable Package | Python, Node.js | 5 min | ⭐⭐ Easy | Advanced users |
| Docker | Docker | 10 min | ⭐⭐⭐ Medium | Tech-savvy |
| Manual | Python, Node.js | 20 min | ⭐⭐⭐⭐ Hard | Developers |

## Conclusion

The Windows Installer is the **best option** for most users:

✅ **No prerequisites** - Everything included  
✅ **Professional** - Standard Windows installer  
✅ **Fast** - 3-4 minutes total  
✅ **Easy** - Click through wizard  
✅ **Clean** - Proper uninstall  

**Recommended for all Windows users!**

---

**Download the installer and start managing your playlists in minutes!** 🎵
