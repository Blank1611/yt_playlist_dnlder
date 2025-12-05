# Old Format Auto-Rename Feature

## Overview

The system now automatically detects and renames video files downloaded in the old format (title only) to the new format (title + video ID).

## Problem

When the filename format changed from:
- **Old**: `Song Title.mp4`
- **New**: `Song Title [dCWj-XGQcXs].mp4`

Videos downloaded before the change would:
1. Exist in `archive.txt` (marked as downloaded)
2. Exist on disk (in old format)
3. Not be detected by new ID-based checking
4. Be re-downloaded unnecessarily

## Solution

### Automatic Detection and Renaming

When checking if a video exists on disk, the system now:

1. **First**: Checks for new format (with video ID in brackets)
   ```
   Song Title [dCWj-XGQcXs].mp4  ✓ Found
   ```

2. **If not found**: Searches for old format (title only)
   ```
   Song Title.mp4  ✓ Found in old format
   ```

3. **Auto-rename**: Converts to new format
   ```
   Song Title.mp4 → Song Title [dCWj-XGQcXs].mp4
   ```

4. **Continue**: Marks as already downloaded (no re-download)

### Smart Title Matching

The system handles various title variations:

#### Exact Match
```
Video Title: "Zubaida"
File on disk: "Zubaida.mp4"
Result: ✓ Exact match → Rename to "Zubaida [dCWj-XGQcXs].mp4"
```

#### Sanitized Match
```
Video Title: "Song: Best Version"
File on disk: "Song Best Version.mp4"  (yt-dlp removed ":")
Result: ✓ Sanitized match → Rename to "Song Best Version [dCWj-XGQcXs].mp4"
```

#### Partial Match
```
Video Title: "Very Long Song Title That Got Truncated"
File on disk: "Very Long Song Title That Got.mp4"
Result: ✓ Partial match → Rename to "Very Long Song Title That Got [dCWj-XGQcXs].mp4"
```

#### Case Insensitive
```
Video Title: "SONG TITLE"
File on disk: "song title.mp4"
Result: ✓ Case-insensitive match → Rename to "song title [dCWj-XGQcXs].mp4"
```

## How It Works

### Function Flow

```python
_video_exists_on_disk(playlist_folder, video_id, video_title)
    ↓
    Check new format: *[video_id]*.mp4
    ↓
    Not found?
    ↓
    _find_video_by_title_and_rename(playlist_folder, video_id, video_title)
        ↓
        1. Try exact sanitized title match
        2. Try original title match
        3. Try fuzzy/partial match
        ↓
        Found? → Rename to new format
        ↓
        Return True (file exists)
```

### Matching Strategy

1. **Exact Sanitized Match**:
   - Sanitizes title (removes invalid chars: `\/:*?"<>|`)
   - Checks for exact filename match

2. **Original Title Match**:
   - Tries original title without sanitization
   - Handles cases where yt-dlp didn't sanitize

3. **Fuzzy Match**:
   - Case-insensitive comparison
   - Partial string matching
   - Prefix matching for truncated names
   - Skips files already in new format

### Safety Features

- **Skip Already Renamed**: Won't rename files that already have `[video_id]` or `_video_id.`
- **Error Handling**: Catches and logs rename failures
- **Non-Destructive**: Only renames, never deletes
- **Logging**: Reports all rename operations

## Usage

### Automatic (Default)

No action needed! The system automatically:
- Detects old format files during download checks
- Renames them on-the-fly
- Continues without re-downloading

### Example Log Output

```
[1/376] Checking: Hindi playlist
  ✓ Renamed old format: Zubaida.mp4 → Zubaida [dCWj-XGQcXs].mp4
  ✓ Already downloaded: Zubaida [dCWj-XGQcXs]

[2/376] Checking: Hindi playlist
  ✓ Renamed old format: Tum Hi Ho.mp4 → Tum Hi Ho [IXaEamvT2Bo].mp4
  ✓ Already downloaded: Tum Hi Ho [IXaEamvT2Bo]
```

## Benefits

✅ **No Re-downloads**: Existing files are recognized and renamed

✅ **Automatic**: Happens transparently during normal operations

✅ **Smart Matching**: Handles sanitized, truncated, and case variations

✅ **Safe**: Only renames, never deletes or overwrites

✅ **Logged**: All renames are reported for transparency

✅ **Backward Compatible**: Works with any old format files

## Technical Details

### Filename Sanitization

The system uses the same sanitization logic as yt-dlp:
```python
def _sanitize_filename(title: str) -> str:
    """Remove invalid filename characters."""
    invalid_chars = r'\/:*?"<>|'
    sanitized = "".join(c for c in title if c not in invalid_chars)
    return sanitized.strip()
```

### Supported Video Extensions

- `.mp4` (most common)
- `.mkv`
- `.webm`
- `.m4v`

### Rename Format

Old format:
```
{title}.{ext}
```

New format:
```
{title} [{video_id}].{ext}
```

Example:
```
Before: "Song Title.mp4"
After:  "Song Title [dCWj-XGQcXs].mp4"
```

## Edge Cases Handled

### 1. Special Characters in Title
```
Title: "Song: The Best (2024)"
Old file: "Song The Best (2024).mp4"
Renamed: "Song The Best (2024) [abc123].mp4"
```

### 2. Very Long Titles
```
Title: "Very Long Song Title That Exceeds Maximum Length..."
Old file: "Very Long Song Title That Exceeds.mp4"
Renamed: "Very Long Song Title That Exceeds [abc123].mp4"
```

### 3. Unicode Characters
```
Title: "गाना नाम"
Old file: "गाना नाम.mp4"
Renamed: "गाना नाम [abc123].mp4"
```

### 4. Duplicate Titles
```
If multiple files match the title, renames the first match found.
Subsequent matches are skipped (already have video ID).
```

## Performance Impact

- **Minimal**: Only searches when file not found by ID
- **One-time**: Each file renamed only once
- **Fast**: Glob pattern matching is efficient
- **Parallel**: Works with parallel startup operations

## Migration Path

### For Existing Users

1. **First Run**: System detects old format files
2. **Auto-Rename**: Converts to new format on-the-fly
3. **Subsequent Runs**: Uses new format (fast ID-based lookup)

### No Manual Action Required

The system handles everything automatically:
- No scripts to run
- No manual renaming needed
- No configuration changes
- Works transparently

## Troubleshooting

### File Not Detected

If a file isn't detected and gets re-downloaded:

1. **Check filename**: Does it match the video title?
2. **Check extension**: Is it .mp4, .mkv, .webm, or .m4v?
3. **Check location**: Is it in the correct playlist folder?
4. **Check logs**: Look for rename attempts in logs

### Rename Failed

If rename fails:
```
⚠️  Could not rename Song.mp4: [Errno 13] Permission denied
```

Possible causes:
- File is open in another program
- Insufficient permissions
- Disk is full or read-only

Solution:
- Close programs using the file
- Check file permissions
- Ensure disk has space

## See Also

- [Custom Archive Logic](CUSTOM_ARCHIVE_IMPROVEMENTS.md) - Archive system
- [Folder Structure](FOLDER_STRUCTURE.md) - File organization
- [Error Classification](ERROR_CLASSIFICATION.md) - Error handling
