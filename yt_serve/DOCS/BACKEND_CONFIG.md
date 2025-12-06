# Backend Configuration

## Overview

The yt_serve backend uses its own configuration system and **does not require config.json**.

## Configuration System

### Settings Location

Settings are managed through:
1. **`.env` file** - Primary configuration (yt_serve/backend/.env)
2. **Pydantic Settings** - Type-safe configuration (app/core/config.py)

### Available Settings

```env
# Download settings
BASE_DOWNLOAD_PATH=downloads
MAX_CONCURRENT_DOWNLOADS=1
MAX_CONCURRENT_EXTRACTIONS=4

# Audio settings
AUDIO_EXTRACT_MODE=copy  # copy, mp3_best, mp3_high, opus

# Batch settings
BATCH_SIZE=200

# Cookies (optional)
COOKIES_FILE=
USE_BROWSER_COOKIES=false
BROWSER_NAME=chrome
```

## How It Works

### 1. Settings Loading

`app/core/config.py` uses Pydantic to load settings from `.env`:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BASE_DOWNLOAD_PATH: str = "downloads"
    AUDIO_EXTRACT_MODE: str = "copy"
    # ... more settings
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 2. Core Module Integration

`app/core/yt_playlist_audio_tools.py` automatically uses backend settings:

```python
from app.core.config import settings

# Use backend settings instead of config.json
BASE_DOWNLOAD_PATH = settings.BASE_DOWNLOAD_PATH
AUDIO_EXTRACT_MODE = settings.AUDIO_EXTRACT_MODE
MAX_EXTRACTION_WORKERS = settings.MAX_CONCURRENT_EXTRACTIONS
```

### 3. Service Layer

`app/services/ytdlp_service.py` imports the configured module:

```python
from app.core import yt_playlist_audio_tools as tools

# Tools module already configured with backend settings
```

## Key Differences from Tkinter Version

| Aspect | Tkinter Version | Web Version (yt_serve) |
|--------|----------------|------------------------|
| Config File | `config.json` | `.env` |
| Config Loading | JSON parsing | Pydantic Settings |
| Location | Root directory | `yt_serve/backend/` |
| Type Safety | No | Yes (Pydantic) |
| Validation | Manual | Automatic |

## Benefits

✅ **No config.json needed** - Uses .env instead  
✅ **Type-safe** - Pydantic validates settings  
✅ **Environment-aware** - Easy deployment  
✅ **Independent** - Doesn't rely on root config  
✅ **Modern** - Follows FastAPI best practices  

## Migration Note

If you're migrating from the Tkinter version:
- Your `config.json` settings should be converted to `.env` format
- The `migrate_from_tkinter.py` script handles this automatically
- Both versions can coexist without conflicts

## Editing Settings

### Option 1: Edit .env file directly
```bash
cd yt_serve/backend
notepad .env  # or your preferred editor
```

### Option 2: Use the web UI
- Settings page in the web interface
- Changes are saved to database and override .env defaults

### Option 3: Environment variables
```bash
# Set environment variables before starting
set BASE_DOWNLOAD_PATH=E:\MyDownloads
python run.py
```

## Troubleshooting

### Settings not loading?
1. Check `.env` file exists in `yt_serve/backend/`
2. Verify syntax (no quotes needed for values)
3. Restart the backend server

### Want to use config.json?
The module has fallback support, but it's not recommended for yt_serve.
The backend is designed to use .env for better deployment practices.
