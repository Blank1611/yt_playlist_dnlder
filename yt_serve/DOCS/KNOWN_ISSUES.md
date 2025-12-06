# Known Issues & Workarounds

## 1. Job Cancellation Behavior (FIXED!)

### Current Behavior
1. User clicks "Cancel"
2. Confirmation dialog appears
3. Cancel flag is set in backend
4. Current video download completes
5. Job stops before next video ✅

### How It Works
- The download service now properly sets `GLOBAL_RUNSTATE.cancelled = True`
- The download loop checks this flag between each video
- Current video completes, then job stops
- Usually takes 10-30 seconds depending on video size

### Note
- Can't interrupt a video mid-download (yt-dlp limitation)
- But will stop before starting the next video
- This is the expected behavior

## 2. Dark Mode Toggle (FIXED)

### Issue
Moon icon not visible in light mode.

### Fix Applied
Changed icon color from `text-gray-700` to `text-gray-700 dark:text-gray-300` so it's visible in both modes.

## 3. Button Visibility During Jobs (FIXED)

### Issue
All buttons visible during download, causing confusion.

### Fix Applied
When a job is running, only the "Cancel" button is shown. All other buttons (Download, Extract, Refresh, Delete) are hidden.

## Tips

### Stopping a Download Quickly
If you need to stop a download immediately:
1. Stop the backend server (Ctrl+C in terminal)
2. Restart the backend
3. The job will be marked as failed

### Monitoring Progress
- Progress bar updates every 2 seconds
- Check backend terminal for detailed logs
- Log files in `{BASE_DOWNLOAD_PATH}/logs/job_{id}.log`

### Best Practices
- Don't start multiple jobs on the same playlist
- Let jobs complete naturally when possible
- Use "Cancel" only when necessary
- Check logs if downloads fail
