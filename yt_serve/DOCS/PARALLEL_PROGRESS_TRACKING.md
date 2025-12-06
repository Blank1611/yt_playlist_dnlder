# Parallel Progress Tracking

## Overview

The system now supports parallel download and audio extraction with separate progress tracking for each phase.

## Features

### 1. Parallel Execution ✅

Download and audio extraction now run in parallel when using "Both" mode:
- Videos are downloaded sequentially
- As videos become available, audio extraction starts in parallel
- Both phases can run simultaneously

### 2. Separate Progress Bars ✅

Two independent progress bars in the UI:
- **📥 Download Progress** - Shows video download progress
- **🎵 Audio Extraction Progress** - Shows audio extraction progress

### 3. Batch Information ✅

Download progress bar displays batch information:
- Current batch progress: "5/10"
- Total progress: "25/100 total (75 remaining)"
- No percentage - just item counts

### 4. Conditional Display ✅

Progress bars only show when active:
- Download bar: Only visible during download phase
- Extraction bar: Only visible during extraction phase
- Completion message: Shows when both phases complete

## Database Schema

### New Job Fields

```sql
-- Download progress
download_status TEXT          -- pending, running, completed, failed
download_total INTEGER         -- Total videos to download
download_completed INTEGER     -- Videos downloaded
download_failed INTEGER        -- Videos that failed
download_batch_info TEXT       -- e.g., "25/100 total (75 remaining)"

-- Extraction progress
extract_status TEXT            -- pending, running, completed, failed
extract_total INTEGER          -- Total videos to extract
extract_completed INTEGER      -- Videos extracted
extract_failed INTEGER         -- Videos that failed extraction
```

## Backend Architecture

### Job Manager

**File:** `app/services/job_manager.py`

**Key Changes:**
```python
async def _run_job(...):
    if job_type == "both":
        # Start both phases in parallel
        download_task = asyncio.create_task(
            self._run_download_phase(...)
        )
        extract_task = asyncio.create_task(
            self._run_extraction_phase(...)
        )
        await asyncio.gather(download_task, extract_task)
```

**New Methods:**
- `_run_download_phase()` - Handles download with progress tracking
- `_run_extraction_phase()` - Handles extraction with progress tracking

### Progress Callbacks

**Download Progress:**
```python
async def download_progress_wrapper(total, current, batch_info=None):
    job.download_total = total
    job.download_completed = current
    job.download_batch_info = batch_info
    job.download_status = "running"
```

**Extraction Progress:**
```python
async def extract_progress_wrapper(total, current):
    job.extract_total = total
    job.extract_completed = current
    job.extract_status = "running"
```

### Core Download Logic

**File:** `app/core/yt_playlist_audio_tools.py`

**Batch Info Generation:**
```python
if needs_batching:
    total_videos = batch_progress["total_videos"]
    downloaded_so_far = batch_progress["downloaded_count"] + idx
    remaining = len(batch_progress["pending_video_ids"])
    batch_info = f"{downloaded_so_far}/{total_videos} total ({remaining} remaining)"

GLOBAL_PROGRESS_CALLBACK(len(current_batch), idx, batch_info)
```

## Frontend Implementation

### TypeScript Types

**File:** `frontend/src/services/types.ts`

```typescript
export interface Job {
  // ... existing fields
  
  // Download progress
  download_status: string | null
  download_total: number
  download_completed: number
  download_failed: number
  download_batch_info: string | null
  
  // Extraction progress
  extract_status: string | null
  extract_total: number
  extract_completed: number
  extract_failed: number
}
```

### Progress Bar Component

**File:** `frontend/src/App.tsx`

```tsx
{/* Download Progress */}
{runningJob.download_status && runningJob.download_status !== 'completed' && (
  <div>
    <div className="flex justify-between text-sm mb-1">
      <span>📥 Downloading</span>
      <span>{runningJob.download_completed} / {runningJob.download_total}</span>
    </div>
    <div className="w-full bg-gray-200 rounded-full h-2">
      <div className="bg-blue-600 h-2 rounded-full" 
           style={{ width: `${progress}%` }} />
    </div>
    {runningJob.download_batch_info && (
      <div className="text-xs text-gray-500">
        {runningJob.download_batch_info}
      </div>
    )}
  </div>
)}

{/* Extraction Progress */}
{runningJob.extract_status && runningJob.extract_status !== 'completed' && (
  <div>
    <div className="flex justify-between text-sm mb-1">
      <span>🎵 Extracting Audio</span>
      <span>{runningJob.extract_completed} / {runningJob.extract_total}</span>
    </div>
    <div className="w-full bg-gray-200 rounded-full h-2">
      <div className="bg-purple-600 h-2 rounded-full" 
           style={{ width: `${progress}%` }} />
    </div>
  </div>
)}
```

## Execution Flow

### "Both" Mode (Parallel)

```
User clicks "Both"
    ↓
Backend creates job
    ↓
Start download_task ──────────┐
    ↓                         │
Download video 1              │
    ↓                         │
Update download progress      │
    ↓                         │
Download video 2              │
    ↓                         │
Update download progress      │
    ↓                         │
...                           │
    ↓                         │
Download complete             │
                              │
                              ├─→ Start extract_task
                              │       ↓
                              │   Wait 5 seconds
                              │       ↓
                              │   Extract video 1
                              │       ↓
                              │   Update extract progress
                              │       ↓
                              │   Extract video 2
                              │       ↓
                              │   Update extract progress
                              │       ↓
                              │   ...
                              │       ↓
                              └───→ Extract complete
                                      ↓
                                  Both complete!
```

### "Download" Mode (Sequential)

```
User clicks "Download"
    ↓
Download video 1
    ↓
Update download progress
    ↓
Download video 2
    ↓
Update download progress
    ↓
...
    ↓
Download complete
```

### "Extract" Mode (Sequential)

```
User clicks "Extract"
    ↓
Extract video 1
    ↓
Update extract progress
    ↓
Extract video 2
    ↓
Update extract progress
    ↓
...
    ↓
Extract complete
```

## UI Examples

### During Download (Both Mode)

```
┌─────────────────────────────────────┐
│ Playlist: My Music                  │
├─────────────────────────────────────┤
│ 📥 Downloading          5 / 10      │
│ ████████░░░░░░░░░░░░░░░░░░░░        │
│ 25/100 total (75 remaining)         │
│                                      │
│ 🎵 Extracting Audio     3 / 5       │
│ ██████████████░░░░░░░░░░░░░░        │
└─────────────────────────────────────┘
```

### During Download Only

```
┌─────────────────────────────────────┐
│ Playlist: My Music                  │
├─────────────────────────────────────┤
│ 📥 Downloading          5 / 10      │
│ ████████░░░░░░░░░░░░░░░░░░░░        │
│ 25/100 total (75 remaining)         │
└─────────────────────────────────────┘
```

### During Extraction Only

```
┌─────────────────────────────────────┐
│ Playlist: My Music                  │
├─────────────────────────────────────┤
│ 🎵 Extracting Audio     8 / 10      │
│ ████████████████████░░░░░░░░        │
└─────────────────────────────────────┘
```

### Completed

```
┌─────────────────────────────────────┐
│ Playlist: My Music                  │
├─────────────────────────────────────┤
│ ✓ Download and extraction completed │
└─────────────────────────────────────┘
```

## Benefits

### Performance
✅ **Parallel execution** - Download and extraction run simultaneously  
✅ **Better resource usage** - CPU and network used efficiently  
✅ **Faster completion** - Overall job completes sooner  

### User Experience
✅ **Clear progress** - Separate bars for each phase  
✅ **Batch information** - Shows total progress across batches  
✅ **No percentages** - Just item counts (more meaningful)  
✅ **Conditional display** - Only shows active phases  

### Maintainability
✅ **Separate concerns** - Download and extraction are independent  
✅ **Better tracking** - Each phase has its own status  
✅ **Easier debugging** - Can see which phase has issues  

## Migration

### Database Migration

Run the migration script to add new fields:

```bash
cd yt_serve/backend
python migrate_db_add_progress_fields.py
```

This adds the new columns to existing jobs table.

### Backward Compatibility

Old fields are kept for compatibility:
- `progress` - Overall progress (deprecated)
- `total_items` - Total items (deprecated)
- `completed_items` - Completed items (deprecated)

New code uses:
- `download_*` fields for download progress
- `extract_*` fields for extraction progress

## Configuration

### Extraction Delay

When running in "both" mode, extraction waits 5 seconds before starting:

```python
# In _run_extraction_phase()
await asyncio.sleep(5)  # Wait for first video to download
```

This can be adjusted based on:
- Average video download time
- Network speed
- Desired parallelism

### Batch Size

Batch size affects the download progress display:

```python
# In .env
BATCH_SIZE=200
```

Larger batches = more videos per session  
Smaller batches = more frequent batch info updates

## Testing

### Test Parallel Execution

1. Add a playlist with 10+ videos
2. Click "Both" button
3. Observe:
   - Download progress bar appears first
   - After ~5 seconds, extraction bar appears
   - Both bars update independently
   - Batch info shows total progress

### Test Download Only

1. Click "Download" button
2. Observe:
   - Only download progress bar shows
   - Batch info displays correctly
   - No extraction bar

### Test Extract Only

1. Click "Extract" button (on playlist with videos)
2. Observe:
   - Only extraction progress bar shows
   - No download bar

## Troubleshooting

### Progress Not Updating

**Check:**
1. Backend logs for progress callback errors
2. Database has new columns (run migration)
3. Frontend polling is working (check Network tab)

### Extraction Not Starting

**Check:**
1. Videos are being downloaded successfully
2. Extraction delay (5 seconds) has passed
3. Backend logs for extraction errors

### Batch Info Not Showing

**Check:**
1. Playlist has more videos than BATCH_SIZE
2. Batch progress file exists in playlist folder
3. Backend is reading batch info correctly

## Future Improvements

Potential enhancements:
- [ ] Configurable extraction delay
- [ ] Real-time WebSocket updates (instead of polling)
- [ ] Per-video progress (0-100% per video)
- [ ] Download speed and ETA
- [ ] Pause/resume functionality
- [ ] Priority queue for extraction

## Related Files

- `yt_serve/backend/app/models/database.py` - Database schema
- `yt_serve/backend/app/services/job_manager.py` - Job orchestration
- `yt_serve/backend/app/services/ytdlp_service.py` - Download service
- `yt_serve/backend/app/core/yt_playlist_audio_tools.py` - Core logic
- `yt_serve/frontend/src/App.tsx` - UI components
- `yt_serve/frontend/src/services/types.ts` - TypeScript types

---

**Implemented:** December 2024  
**Features:** Parallel execution, separate progress bars, batch info  
**Status:** ✅ Complete and tested
