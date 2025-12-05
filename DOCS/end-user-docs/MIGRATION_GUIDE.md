# Migration Guide: Tkinter → Web Backend

## Overview

This guide helps you migrate your existing playlists and configuration from the Tkinter app to the new web backend.

## What Gets Migrated

✅ **Playlists**
- URL
- Title
- Local count
- Playlist count
- Unavailable count
- Excluded video IDs
- Last download timestamp
- Last extract timestamp

✅ **Configuration**
- Base download path (already in .env)

## Prerequisites

1. **Backend setup complete**
   ```bash
   cd yt_serve/backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment configured**
   - `.env` file exists with correct `BASE_DOWNLOAD_PATH`
   - Should match the path in `yt_playlist_gui_config.json`

## Migration Steps

### Step 1: Verify Base Path

Check that your `.env` file has the correct path:

```bash
# In yt_serve/backend/.env
BASE_DOWNLOAD_PATH=E:\\2tbhdd\\songs\\syst\\New folder\\youtube
```

This should match the `base_path` in your `yt_playlist_gui_config.json`.

### Step 2: Run Migration Script

From the **project root** directory:

```bash
python migrate_playlists.py
```

The script will automatically find `yt_playlist_gui_config.json` in the project root.

**Note:** There are two migration scripts:
- `migrate_playlists.py` - Simple script in project root (recommended)
- `yt_serve/backend/migrate_from_tkinter.py` - Full-featured version

### Step 3: Review Migration

The script will show:
- Number of playlists found
- Each playlist being added/updated
- Summary of changes

Example output:
```
============================================================
TKINTER APP → WEB BACKEND MIGRATION
============================================================

Loading config from: ../../yt_playlist_gui_config.json

Old base path: E:\2tbhdd\songs\syst\New folder\youtube
Current base path: E:\2tbhdd\songs\syst\New folder\youtube

Found 0 existing playlists in database
Found 19 playlists in config file

✅ Adding: Hindi Old hits
   URL: https://www.youtube.com/playlist?list=PLzREdHub6okcd1PfRreU3VE6WGxZJABnC
   Local: 126, Playlist: 126, Unavailable: 3
   Excluded IDs: 2

✅ Adding: Just mood hindi
   URL: https://www.youtube.com/playlist?list=PLzREdHub6okf2igkHjLNxmXQzM_UrwgDE
   Local: 54, Playlist: 54, Unavailable: 0
   Excluded IDs: 0

... (more playlists)

============================================================
MIGRATION COMPLETE
============================================================
✅ Added: 19 playlists
📝 Updated: 0 playlists
⏭️  Skipped: 0 playlists
📊 Total: 19 playlists
============================================================

📋 Next Steps:
1. Start the backend: python run.py
2. Open API docs: http://localhost:8000/docs
3. View playlists: GET /api/playlists
4. Start downloads: POST /api/downloads/jobs
```

### Step 4: Verify Migration

Start the backend:

```bash
python run.py
```

Open the API docs: http://localhost:8000/docs

Test the playlists endpoint:
```bash
curl http://localhost:8000/api/playlists
```

You should see all your playlists!

## Migration Behavior

### New Playlists
- Creates new database entries
- Preserves all metadata
- Converts IST timestamps to UTC

### Existing Playlists
- Updates metadata (counts, excluded IDs)
- Updates timestamps if newer
- Preserves database ID

### Safe to Re-run
- Running the script multiple times is safe
- Existing playlists will be updated, not duplicated
- No data loss

## Troubleshooting

### Base Path Mismatch

If the paths don't match:

```
⚠️  WARNING: Base paths don't match!
Old: E:\2tbhdd\songs\syst\New folder\youtube
New: D:\Music\YouTube Playlists

Continue anyway? (y/n):
```

**Options:**
1. Update `.env` to match old path
2. Continue anyway (if you moved files)
3. Cancel and fix paths first

### Config File Not Found

```
❌ Config file not found!
   Looked in: ../../yt_playlist_gui_config.json

Usage:
   python migrate_from_tkinter.py [path/to/yt_playlist_gui_config.json]
```

**Solution:** Provide the full path:
```bash
python migrate_from_tkinter.py C:\path\to\yt_playlist_gui_config.json
```

### Database Locked

If you get "database is locked" error:
1. Stop the backend server
2. Run migration again
3. Restart backend

## After Migration

### Both Apps Can Coexist

The web backend and Tkinter app can run side-by-side:
- Both use the same download folders
- Both use the same archive system
- Both respect excluded IDs

### Recommended Workflow

1. **Use web backend for new operations**
   - Better performance
   - Real-time updates
   - Non-blocking

2. **Keep Tkinter app as backup**
   - Familiar interface
   - Proven stability
   - Quick access

3. **Sync periodically**
   - Re-run migration to sync changes
   - Or use web backend exclusively

## Data Mapping

| Tkinter Config | Database Field | Notes |
|----------------|----------------|-------|
| url | url | Unique identifier |
| title | title | Playlist name |
| local_count | local_count | Files on disk |
| playlist_count | playlist_count | Videos in playlist |
| unavailable_count | unavailable_count | Deleted/private videos |
| excluded_ids | excluded_ids | JSON array |
| last_download_ist | last_download | Converted to UTC |
| last_extract_ist | last_extract | Converted to UTC |
| base_path | .env setting | Not in database |

## Rollback

If you need to rollback:

1. **Delete database:**
   ```bash
   del yt_manager.db
   ```

2. **Restart backend:**
   ```bash
   python run.py
   ```

3. **Re-run migration:**
   ```bash
   python migrate_from_tkinter.py
   ```

## Next Steps

After successful migration:

1. ✅ **Test API** - Try listing playlists
2. ✅ **Start a job** - Download a small playlist
3. ✅ **Check logs** - Verify logging works
4. ✅ **Build frontend** - Or use API directly

## Questions?

- Check [TESTING_GUIDE.md](TESTING_GUIDE.md) for API examples
- Check [COMPLETE.md](COMPLETE.md) for architecture details
- Check [LOGGING_ARCHITECTURE.md](LOGGING_ARCHITECTURE.md) for log details

---

**Ready to migrate?** Run the script and watch your playlists transfer! 🚀
