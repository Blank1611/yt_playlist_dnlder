# Logs Viewer

## Overview

The UI now includes a built-in logs viewer that displays real-time job logs directly in the web interface.

## Features

### 1. View Logs Button ✅
- Appears below the progress bars for running jobs
- Click to open the logs modal
- Shows logs for the current job

### 2. Real-Time Updates ✅
- Auto-refreshes every 2 seconds while job is running
- Stops refreshing when job completes
- Auto-scrolls to latest log entry

### 3. Copy to Clipboard ✅
- "Copy Logs" button to copy all logs
- Useful for sharing or debugging
- One-click operation

### 4. Clean Interface ✅
- Monospace font for easy reading
- Dark mode support
- Scrollable log area
- Shows job status and ID

## Usage

### Viewing Logs

1. Start a download/extract job
2. Look for the "View Logs" button below the progress bars
3. Click "View Logs" to open the modal
4. Logs will auto-refresh while the job is running

### Copying Logs

1. Open the logs modal
2. Click "Copy Logs" button in the top-right
3. Logs are copied to clipboard
4. Paste anywhere (email, bug report, etc.)

### Closing Logs

- Click the X button in the top-right
- Or click outside the modal

## UI Components

### View Logs Button

Located below progress bars:
```tsx
<button onClick={() => setViewingLogs(runningJob)}>
  <LogIcon /> View Logs
</button>
```

### Logs Modal

Full-screen modal with:
- **Header**: Job info (ID, type, status)
- **Body**: Scrollable log area with monospace font
- **Footer**: Auto-refresh status and log count
- **Actions**: Copy logs, close modal

## Technical Details

### Auto-Refresh

```typescript
const { data: logs } = useQuery({
  queryKey: ['logs', job.id],
  queryFn: async () => {
    const res = await jobsApi.logs(job.id, 100)
    return res.data
  },
  refetchInterval: job.status === 'running' ? 2000 : false,
})
```

- Refreshes every 2 seconds if job is running
- Stops refreshing when job completes
- Fetches last 100 log lines

### Auto-Scroll

```typescript
const logsEndRef = useRef<HTMLDivElement>(null)

useEffect(() => {
  logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
}, [logs])
```

- Automatically scrolls to bottom when logs update
- Smooth scrolling animation
- Keeps latest logs visible

### Copy to Clipboard

```typescript
const copyLogs = () => {
  const logText = logs.map(l => l.message).join('\n')
  navigator.clipboard.writeText(logText)
  alert('Logs copied to clipboard!')
}
```

## Log Format

Logs are displayed as plain text with timestamps:

```
[2024-12-07 10:30:15] Starting download for playlist: My Music
[2024-12-07 10:30:16] [1/10] Downloading: video_id_1
[2024-12-07 10:30:20]   ✓ Download verified, adding video_id_1 to archive
[2024-12-07 10:30:21] [2/10] Downloading: video_id_2
[2024-12-07 10:30:25]   ✓ Download verified, adding video_id_2 to archive
...
```

## API Endpoint

The logs are fetched from:

```
GET /api/downloads/jobs/{job_id}/logs?lines=100
```

**Parameters:**
- `job_id`: The job ID
- `lines`: Number of lines to return (default: all)

**Response:**
```json
[
  { "message": "[2024-12-07 10:30:15] Starting download..." },
  { "message": "[2024-12-07 10:30:16] [1/10] Downloading..." }
]
```

## Styling

### Light Mode
- White background
- Gray text
- Blue accents
- Clean, professional look

### Dark Mode
- Dark gray background
- Light gray text
- Blue accents
- Easy on the eyes

### Monospace Font
- Uses `font-mono` class
- Easy to read logs
- Aligns timestamps
- Professional appearance

## Examples

### During Download

```
┌─────────────────────────────────────────────────────┐
│ Job Logs                                    [Copy] X │
│ Job #1 - both - running                             │
├─────────────────────────────────────────────────────┤
│ [2024-12-07 10:30:15] Starting download...         │
│ [2024-12-07 10:30:16] [1/10] Downloading: vid_1    │
│ [2024-12-07 10:30:20]   ✓ Download verified        │
│ [2024-12-07 10:30:21] [2/10] Downloading: vid_2    │
│ [2024-12-07 10:30:25]   ✓ Download verified        │
│ [2024-12-07 10:30:26] Starting extraction...       │
│ [2024-12-07 10:30:27] Extracting audio from vid_1  │
│ ...                                                  │
├─────────────────────────────────────────────────────┤
│ 🔄 Auto-refreshing every 2 seconds    7 log entries │
└─────────────────────────────────────────────────────┘
```

### After Completion

```
┌─────────────────────────────────────────────────────┐
│ Job Logs                                    [Copy] X │
│ Job #1 - both - completed                           │
├─────────────────────────────────────────────────────┤
│ [2024-12-07 10:30:15] Starting download...         │
│ ...                                                  │
│ [2024-12-07 10:35:42] Download completed           │
│ [2024-12-07 10:35:43] Extraction completed         │
│ [2024-12-07 10:35:44] Job completed successfully   │
├─────────────────────────────────────────────────────┤
│ ✓ Job completed                           15 log entries │
└─────────────────────────────────────────────────────┘
```

## Benefits

### For Users
✅ **Easy access** - View logs directly in UI  
✅ **Real-time** - See progress as it happens  
✅ **Copy/paste** - Share logs easily  
✅ **No terminal** - No need to check backend console  

### For Debugging
✅ **Detailed info** - See exactly what's happening  
✅ **Error messages** - Catch issues immediately  
✅ **Progress tracking** - Monitor download progress  
✅ **Timestamps** - Know when things happened  

### For Support
✅ **Easy sharing** - Copy logs to clipboard  
✅ **Complete history** - All job events logged  
✅ **Professional** - Clean, readable format  

## Keyboard Shortcuts

- **Esc**: Close modal (future enhancement)
- **Ctrl+C**: Copy logs (future enhancement)

## Future Enhancements

Potential improvements:
- [ ] Search/filter logs
- [ ] Download logs as file
- [ ] Syntax highlighting for errors
- [ ] Keyboard shortcuts
- [ ] Log levels (info, warning, error)
- [ ] Expand/collapse sections
- [ ] Live streaming (WebSocket)

## Troubleshooting

### Logs Not Showing

**Check:**
1. Job has started (logs are created when job runs)
2. Backend is running
3. Log files exist in `backend/downloads/logs/`
4. API endpoint is accessible

### Auto-Refresh Not Working

**Check:**
1. Job status is "running"
2. React Query is configured correctly
3. No network errors in browser console

### Copy Not Working

**Check:**
1. Browser supports clipboard API
2. Page is served over HTTPS (or localhost)
3. User granted clipboard permissions

## Related Files

- `yt_serve/frontend/src/App.tsx` - LogsModal component
- `yt_serve/backend/app/services/job_manager.py` - Log writing
- `yt_serve/backend/app/api/downloads.py` - Logs endpoint
- `yt_serve/frontend/src/services/api.ts` - API client

---

**Implemented:** December 2024  
**Features:** Real-time logs, auto-refresh, copy to clipboard  
**Status:** ✅ Complete and ready to use
