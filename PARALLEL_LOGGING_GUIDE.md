# Parallel Processing Logging Guide

## Overview
With parallel processing enabled for both startup operations and audio extraction, logs now include timestamps and thread IDs for better traceability.

## Log Format

### Startup Operations
```
[HH:MM:SS] [ThreadPoolExecutor-X_Y] [Playlist Name] Message
```

**Example:**
```
[16:03:22] [ThreadPoolExecutor-0_0] [Awesome] Checking folder structure
[16:03:22] [ThreadPoolExecutor-0_1] [Hindi Old hits] Checking folder structure
[16:03:22] [ThreadPoolExecutor-0_2] [Woo] Checking folder structure
[16:03:22] [ThreadPoolExecutor-0_3] [Just music] Checking folder structure
[16:03:22] [ThreadPoolExecutor-0_4] [Energy] Checking folder structure
[16:03:23] [ThreadPoolExecutor-0_0] [Awesome] ✓ playlist_info.json exists
[16:03:23] [ThreadPoolExecutor-0_0] [Awesome] Refreshing stats...
[16:03:24] [ThreadPoolExecutor-0_1] [Hindi Old hits] ✓ playlist_info.json exists
[16:03:27] [ThreadPoolExecutor-0_0] [Awesome] ✓ Stats: 595 local, 599 available, 4 unavailable
```

### Audio Extraction
```
[HH:MM:SS] [ThreadPoolExecutor-X_Y] [idx/total] Action: filename
```

**Example:**
```
[16:15:30] [ThreadPoolExecutor-1_0] [1/595] Extracting (copy): Video1.mp4
[16:15:30] [ThreadPoolExecutor-1_1] [2/595] Extracting (copy): Video2.mp4
[16:15:30] [ThreadPoolExecutor-1_2] [3/595] Extracting (copy): Video3.mp4
[16:15:30] [ThreadPoolExecutor-1_3] [4/595] Extracting (copy): Video4.mp4
[16:15:31] [ThreadPoolExecutor-1_0] [1/595] ✓ Completed in 0.8s: Video1.m4a
[16:15:31] [ThreadPoolExecutor-1_0] [5/595] Extracting (copy): Video5.mp4
[16:15:32] [ThreadPoolExecutor-1_2] [3/595] ✓ Completed in 1.2s: Video3.m4a
```

## Log Components

### 1. Timestamp `[HH:MM:SS]`
- Shows exact time when log entry was created
- Helps track operation duration
- Useful for identifying bottlenecks

### 2. Thread ID `[ThreadPoolExecutor-X_Y]`
- `X` = Executor instance number
- `Y` = Worker thread number (0 to max_workers-1)
- Helps trace which thread processed which item
- Useful for debugging thread-specific issues

### 3. Context Identifier
- **Startup**: `[Playlist Name]` - Which playlist is being processed
- **Extraction**: `[idx/total]` - Progress indicator (e.g., [42/595])

### 4. Status Symbols
- `✓` - Success
- `⚠️` - Warning or error
- No symbol - In progress

## Reading Parallel Logs

### Understanding Thread Interleaving
Logs from different threads will be interleaved (mixed together). This is normal and expected:

```
[16:03:22] [ThreadPoolExecutor-0_0] [Awesome] Checking folder structure
[16:03:22] [ThreadPoolExecutor-0_1] [Hindi] Checking folder structure
[16:03:23] [ThreadPoolExecutor-0_0] [Awesome] ✓ Stats: 595 local
[16:03:23] [ThreadPoolExecutor-0_2] [Woo] Checking folder structure
[16:03:24] [ThreadPoolExecutor-0_1] [Hindi] ✓ Stats: 120 local
```

### Filtering Logs by Thread
To see what a specific thread did, filter by thread ID:
```bash
# Windows PowerShell
Get-Content logs\app_startup.log | Select-String "ThreadPoolExecutor-0_0"

# Or search for specific playlist
Get-Content logs\app_startup.log | Select-String "\[Awesome\]"
```

### Filtering Logs by Playlist
```bash
# See all operations for "Awesome" playlist
Get-Content logs\app_startup.log | Select-String "\[Awesome\]"
```

### Timeline Analysis
Sort by timestamp to see chronological order:
```bash
# Logs are already in chronological order
Get-Content logs\app_startup.log | Select-String "16:03"
```

## Performance Metrics

### Startup Summary
At the end of startup, you'll see:
```
✓ Completed refresh of 19 playlists in 8.3 seconds
```

### Extraction Summary
At the end of extraction, you'll see:
```
============================================================
Audio extraction summary:
  Total processed: 595/595
  Newly extracted: 590
  Skipped (already exist): 5
  Failed: 0
  Time taken: 148.3 seconds
  Average: 0.3 sec/file
============================================================
```

## Troubleshooting

### Finding Errors
Search for warning symbol:
```bash
Get-Content logs\app_startup.log | Select-String "⚠️"
```

### Finding Slow Operations
Look for large time gaps between timestamps for the same thread:
```
[16:03:22] [ThreadPoolExecutor-0_0] [Awesome] Refreshing stats...
[16:03:45] [ThreadPoolExecutor-0_0] [Awesome] ✓ Stats: 595 local
# 23 seconds - this playlist took a long time
```

### Thread Utilization
Count how many threads are active:
```bash
# Count unique thread IDs in recent logs
Get-Content logs\app_startup.log | Select-String "ThreadPoolExecutor" | 
  ForEach-Object { $_ -match '\[ThreadPoolExecutor-\d+_(\d+)\]' | Out-Null; $matches[1] } | 
  Sort-Object -Unique
```

## Benefits of Enhanced Logging

1. **Traceability**: Know exactly which thread processed which item
2. **Debugging**: Identify thread-specific issues
3. **Performance Analysis**: See which operations take longest
4. **Monitoring**: Track progress of parallel operations in real-time
5. **Troubleshooting**: Quickly find errors or warnings
6. **Optimization**: Identify bottlenecks and optimize worker count
