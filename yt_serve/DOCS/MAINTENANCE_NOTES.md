# yt_serve Maintenance Notes

## Important: Backend Core Module

### Custom Version

The file `yt_serve/backend/app/core/yt_playlist_audio_tools.py` is a **customized version** that differs from the root `yt_playlist_audio_tools.py`.

**Key Differences:**
- Uses backend's Pydantic settings (from `.env`)
- Imports `app.core.config.settings`
- Falls back to `config.json` only in standalone mode
- Dual-mode support for both backend and standalone usage

### DO NOT Overwrite

⚠️ **Warning:** Do not copy the root version over the backend version!

The backend version has been modified to:
1. Use `.env` configuration via Pydantic
2. Work independently without `config.json`
3. Support both backend and standalone modes

### Protection Mechanism

The `reorganize_project.py` script has been updated to protect the customized version:

```python
# Check if backend core module exists (don't overwrite if already customized)
dest = yt_serve / "backend" / "app" / "core" / "yt_playlist_audio_tools.py"
if dest.exists():
    print("✓ Keeping customized version")
elif src.exists():
    shutil.copy2(str(src), str(dest))
```

### Updating the Backend Version

If you need to update the backend's `yt_playlist_audio_tools.py`:

**Option 1: Manual Merge (Recommended)**
1. Check what changed in root version
2. Manually apply relevant changes to backend version
3. Keep the configuration system intact (lines 1-80)

**Option 2: Re-apply Configuration Changes**
1. Copy from root if needed
2. Re-apply the backend settings integration:
   - Import `app.core.config.settings`
   - Add `_USE_BACKEND_SETTINGS` flag
   - Use settings instead of CONFIG dict

### Configuration System Code

The backend version includes this configuration system (keep this intact):

```python
# Import backend settings instead of loading config.json
try:
    from app.core.config import settings
    _USE_BACKEND_SETTINGS = True
except ImportError:
    _USE_BACKEND_SETTINGS = False
    settings = None

# Load config only if backend settings not available
CONFIG = {} if _USE_BACKEND_SETTINGS else _load_config()

# Use backend settings when available
if _USE_BACKEND_SETTINGS and settings:
    BASE_DOWNLOAD_PATH = settings.BASE_DOWNLOAD_PATH
    AUDIO_EXTRACT_MODE = settings.AUDIO_EXTRACT_MODE
    # ... etc
else:
    # Fallback to config.json
    BASE_DOWNLOAD_PATH = CONFIG.get("base_download_path")
    # ... etc
```

## Syncing Changes Between Versions

### Root → Backend

When updating functionality in root `yt_playlist_audio_tools.py`:

1. **Identify the change** - What functions/logic changed?
2. **Check configuration** - Does it involve config values?
3. **Apply to backend** - Copy the logic changes only
4. **Keep config system** - Don't overwrite the configuration code
5. **Test** - Verify backend still uses `.env` settings

### Backend → Root

When adding backend-specific features:

1. **Evaluate need** - Does Tkinter version need this?
2. **Remove backend deps** - Strip out Pydantic/FastAPI code
3. **Use config.json** - Ensure it uses CONFIG dict
4. **Test standalone** - Verify Tkinter version works

## Testing After Updates

### Test Backend Settings Integration

```bash
cd yt_serve/backend
python -c "from app.core import yt_playlist_audio_tools as tools; print('Backend mode:', tools._USE_BACKEND_SETTINGS); print('Base path:', tools.BASE_DOWNLOAD_PATH)"
```

Expected:
```
Backend mode: True
Base path: downloads  # or your .env value
```

### Test Standalone Mode

```bash
cd /some/other/directory
python -c "import sys; sys.path.insert(0, 'path/to/root'); import yt_playlist_audio_tools as tools; print('Backend mode:', tools._USE_BACKEND_SETTINGS)"
```

Expected:
```
Backend mode: False
```

## Common Mistakes to Avoid

❌ **Don't:** Run `shutil.copy2('yt_playlist_audio_tools.py', 'yt_serve/backend/app/core/')`  
✅ **Do:** Manually merge changes or use the protected reorganize script

❌ **Don't:** Remove the `try/except ImportError` for settings  
✅ **Do:** Keep dual-mode support for flexibility

❌ **Don't:** Hard-code paths or settings in backend version  
✅ **Do:** Use `settings.SETTING_NAME` for all configuration

## Version Tracking

To track which version of the core module is in use:

```python
# Add to backend version
__version__ = "2.0.0-backend"
__config_mode__ = "pydantic"

# Add to root version  
__version__ = "2.0.0-standalone"
__config_mode__ = "json"
```

## Questions?

If you're unsure whether to update the backend version:
1. Check if the change is configuration-related → Keep backend as-is
2. Check if it's core download logic → Safe to merge
3. Check if it adds new features → Evaluate case-by-case

When in doubt, test both versions after changes!
