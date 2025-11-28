# YouTube Playlist Audio Tools

A Python application to download YouTube playlists and extract audio as MP3 files with a GUI manager.

## Features

- Download YouTube playlists with best video + audio quality
- Automatically extract audio to MP3 format
- GUI-based playlist manager with stats tracking
- Per-playlist exclusion list for unavailable videos
- Logging system for all operations
- Archive system to avoid re-downloading

## System Requirements

- Python 3.8+
- FFmpeg (for audio extraction)
- Windows/Mac/Linux

## Installation

### 1. Clone or download this project

```bash
cd testyoutube
```

### 2. Create a Python virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**On Windows:**
```bash
venv\Scripts\activate
```

**On Mac/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 5. Install FFmpeg

FFmpeg is required to extract audio from video files.

**On Windows:**
- **Option A (Automatic via Chocolatey):**
  ```bash
  choco install ffmpeg
  ```
  (Install Chocolatey first if you don't have it: https://chocolatey.org/install)

- **Option B (Manual):**
  1. Download from https://ffmpeg.org/download.html
  2. Extract to a folder (e.g., `C:\ffmpeg`)
  3. Add the `bin` folder to your Windows PATH:
     - Right-click "This PC" → Properties
     - Click "Advanced system settings"
     - Click "Environment Variables"
     - Under "System variables", find "Path" and click "Edit"
     - Click "New" and add: `C:\ffmpeg\bin`
     - Click OK and restart your terminal

**On Mac:**
```bash
brew install ffmpeg
```

**On Linux (Ubuntu/Debian):**
```bash
sudo apt-get install ffmpeg
```

### 6. Configure the application

Edit `config.json` with your settings:

```json
{
  "base_download_path": "/path/to/youtube/downloads",
  "cookies_file": "/path/to/yt-cookies.txt"
}
```

#### Configuration Variables

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `base_download_path` | String | Root directory where playlists will be downloaded | `"E:\\Downloads\\youtube"` or `"/home/user/youtube"` |
| `cookies_file` | String | Path to YouTube cookies file for authenticated downloads (optional) | `"C:\\cookies\\yt-cookies.txt"` |

**Note:** 
- Use forward slashes `/` or double backslashes `\\` for Windows paths in JSON
- If you don't have a cookies file, leave it as-is or provide a valid path. The app will work without it for public videos.
- To get cookies: Use a browser extension like "Get cookies.txt LOCALLY" and save it

## Usage

### Running the GUI Manager

```bash
python yt_playlist_manager_gui_final.py
```

The GUI will:
1. Display all saved playlists in a table
2. Show stats: local videos, available videos, unavailable videos
3. Let you add/remove playlists
4. Perform download or extract operations

### Running the Audio Tools Directly

```python
import yt_playlist_audio_tools as tools

# Download a playlist and extract audio
failed_ids = tools.download_playlist_with_video_and_audio(
    url="https://www.youtube.com/playlist?list=...",
    as_mp3=True
)

# Extract audio from already-downloaded videos
tools.extract_audio_for_existing_playlist(title="My Playlist")
```

## File Structure

```
testyoutube/
├── config.json                          # Main config file (edit this!)
├── requirements.txt                     # Python dependencies
├── README.md                            # This file
├── yt_playlist_audio_tools.py          # Core download/extract logic
├── yt_playlist_manager_gui_final.py    # GUI application
├── yt_playlist_gui_config.json         # Auto-generated (GUI state)
└── logs/                               # Auto-generated (operation logs)
    ├── app_startup.log
    └── {playlist_name}.log
```

## Logs

All operations are logged to the `logs/` folder:
- `app_startup.log` — Startup operations
- `{playlist_name}.log` — Individual playlist operations

Check these files if something goes wrong.

## Troubleshooting

### "FFmpeg not found"
- Verify FFmpeg is installed: `ffmpeg -version`
- Check it's in your PATH (restart terminal after adding to PATH)

### "Config file not found"
- Ensure `config.json` exists in the same directory as the scripts
- Check the file path is correct

### Videos not downloading
- Check if the playlist URL is correct
- Try without cookies file first (remove it from config if present)
- Check logs in `logs/` folder for error details

### Audio extraction fails
- Ensure FFmpeg is properly installed
- Check that video files exist in the download folder
- Check logs for specific error messages

## Advanced Usage

### Excluding unavailable videos
The GUI allows you to manually mark video IDs as unavailable:
1. Select a playlist in the table
2. Click "Edit exclusions for selected"
3. Enter video IDs (one per line)

These IDs won't be counted as "available" when checking playlist stats.

## License

Provided as-is for personal use.

## Support

Check the logs folder for detailed error messages if you encounter issues.