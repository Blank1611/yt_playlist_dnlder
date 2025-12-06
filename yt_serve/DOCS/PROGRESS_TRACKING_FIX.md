# Progress Tracking Fix

## Issue

The progress bar in the UI was staying at 0.0% during video downloads, even though downloads were progressing normally.

## Root Causes

### 1. Missing Progress Callbacks in Download Loop

The `download_playlist_with_video_and_audio()` function in `yt_playlist_audio_tools.py` was not calling `GLOBAL_PROGRESS_CALLBACK` during the download loop. It only called it during audio extraction.

**Before:**
```python
for idx, (vid, video_url) in enumerate(current_batch, 1):
    # No progress callback here!
    ydl.download([video_url])
    # ...
```

**After:**
```python
for idx, (vid, video_url) in enumerate(current_batch, 1):
    # Update progress BEFORE downloading
    if GLOBAL_PROGRESS_CALLBACK is not None:
        GLOBAL_PROGRESS_CALLBACK(len(current_batch), idx - 1)
    
    ydl.download([video_url])
    
    # Update progress AFTER successful download
    if GLOBAL_PROGRESS_CALLBACK is not None:
        GLOBAL_PROGRESS_CALLBACK(len(current_batch), idx)
```

### 2. Thread-Safety Issue with Async Callbacks

The progress callback was being called from a thread pool executor (where yt-dlp runs), but it was trying to create tasks in the main event loop using `loop.create_task()`, which doesn't work across threads.

**Before:**
```python
def sync_progress(total, current):
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(async_progress(total, current))  # ❌ Doesn't work from thread!
    except RuntimeError:
        pass
```

**After:**
```python
def sync_progress(total, current):
    try:
        # Use asyncio.run_coroutine_threadsafe for thread-safe callback
        asyncio.run_coroutine_threadsafe(
            progress_callback(total, current),
            main_loop
        )
    except Exception as e:
        print(f"Progress callback error: {e}")
```

## Changes Made

### 1. Updated `yt_playlist_audio_tools.py`

**File:** `yt_serve/backend/app/core/yt_playlist_audio_tools.py`

Added progress callback calls in the download loop:
- Before each download: `GLOBAL_PROGRESS_CALLBACK(total, current - 1)`
- After successful download: `GLOBAL_PROGRESS_CALLBACK(total, current)`
- After failed download: `GLOBAL_PROGRESS_CALLBACK(total, current)`

This ensures the UI is updated as each video is downloaded.

### 2. Updated `ytdlp_service.py`

**File:** `yt_serve/backend/app/services/ytdlp_service.py`

Fixed both `download_playlist()` and `extract_audio()` methods to use `asyncio.run_coroutine_threadsafe()` instead of `loop.create_task()`.

**Key changes:**
```python
# Store the main event loop
main_loop = asyncio.get_event_loop()

def sync_progress(total, current):
    # Use run_coroutine_threadsafe for thread-safe execution
    asyncio.run_coroutine_threadsafe(
        progress_callback(total, current),
        main_loop
    )
```

## How It Works Now

### Download Flow

```
1. User clicks "Download" button
   ↓
2. Frontend sends request to backend
   ↓
3. Backend creates job with progress_callback
   ↓
4. Job manager starts download in thread pool
   ↓
5. For each video:
   - Call progress_callback(total, current-1)  ← Before download
   - Download video with yt-dlp
   - Call progress_callback(total, current)    ← After download
   ↓
6. Progress callback uses run_coroutine_threadsafe
   ↓
7. Main event loop updates database
   ↓
8. Frontend polls /api/downloads/jobs
   ↓
9. UI updates progress bar
```

### Thread Safety

```
Thread Pool (yt-dlp)          Main Event Loop (FastAPI)
─────────────────────         ──────────────────────────
Download video 1
  ↓
Call sync_progress(10, 1)
  ↓
  run_coroutine_threadsafe() ──→ Schedule coroutine
                                    ↓
                                  Execute progress_callback
                                    ↓
                                  Update database
                                    ↓
Download video 2                  Return to event loop
  ↓
Call sync_progress(10, 2)
  ↓
  run_coroutine_threadsafe() ──→ Schedule coroutine
                                    ↓
                                  Execute progress_callback
                                    ↓
                                  Update database
```

## Testing

### Verify Progress Updates

1. Start the backend:
```bash
cd yt_serve/backend
python run.py
```

2. Start the frontend:
```bash
cd yt_serve/frontend
npm run dev
```

3. Add a playlist and click "Download"

4. Watch the progress bar - it should now update as each video downloads:
   - 0% → 10% → 20% → ... → 100%

### Expected Behavior

- **Before download starts:** 0%
- **During downloads:** Progress increases with each video (e.g., 1/10 = 10%, 2/10 = 20%)
- **After downloads complete:** 100%

### Debug Output

The backend console should show:
```
[1/10] Downloading: video_id_1
  ✓ Download verified, adding video_id_1 to archive
[2/10] Downloading: video_id_2
  ✓ Download verified, adding video_id_2 to archive
...
```

And the database should update after each video.

## Technical Details

### asyncio.run_coroutine_threadsafe()

This function is specifically designed for calling async functions from other threads:

```python
asyncio.run_coroutine_threadsafe(coro, loop)
```

**Parameters:**
- `coro`: The coroutine to execute
- `loop`: The event loop to execute it in

**Returns:**
- A `concurrent.futures.Future` object

**Thread Safety:**
- ✅ Safe to call from any thread
- ✅ Schedules coroutine in the specified event loop
- ✅ Returns immediately (non-blocking)

### Why loop.create_task() Didn't Work

`loop.create_task()` can only be called from the same thread that's running the event loop:

```python
# ❌ This fails when called from thread pool:
loop = asyncio.get_event_loop()
loop.create_task(my_coroutine())  # RuntimeError!

# ✅ This works from any thread:
asyncio.run_coroutine_threadsafe(my_coroutine(), loop)
```

## Related Files

- `yt_serve/backend/app/core/yt_playlist_audio_tools.py` - Download logic
- `yt_serve/backend/app/services/ytdlp_service.py` - Service wrapper
- `yt_serve/backend/app/services/job_manager.py` - Job management
- `yt_serve/backend/app/api/downloads.py` - API endpoints

## Future Improvements

Potential enhancements:
- [ ] Add sub-progress for individual video download (0-100% per video)
- [ ] Show download speed and ETA
- [ ] Add progress for audio extraction phase
- [ ] Persist progress to database more frequently
- [ ] Add WebSocket for real-time progress updates (instead of polling)

## References

- **[asyncio.run_coroutine_threadsafe](https://docs.python.org/3/library/asyncio-task.html#asyncio.run_coroutine_threadsafe)** - Python docs
- **[Threading and asyncio](https://docs.python.org/3/library/asyncio-dev.html#concurrency-and-multithreading)** - Best practices
- **[FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)** - FastAPI guide

---

**Fixed:** December 2024  
**Issue:** Progress bar stuck at 0%  
**Status:** ✅ Resolved
