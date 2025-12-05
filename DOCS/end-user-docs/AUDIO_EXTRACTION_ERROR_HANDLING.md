# Audio Extraction Error Handling

## Overview

The audio extraction process now includes robust error handling and automatic fallback strategies for problematic video files.

## Common Errors

### Error Code 4294967274 (or -22)

**Meaning**: Invalid argument or incompatible audio stream

**Common Causes**:
1. Video has no audio stream
2. Audio codec incompatible with `.m4a` container in copy mode
3. Corrupted video file
4. Incomplete download
5. Old videos downloaded with different settings

**Solution**: Automatic fallback to re-encoding

### Why It Happens for Old Downloads Only

**New downloads** (current settings):
- yt-dlp downloads with `bestvideo+bestaudio/best`
- Merges into MP4 with compatible audio (usually AAC)
- Audio can be copied to `.m4a` without issues

**Old downloads** (previous settings or different sources):
- May have different audio codecs
- Audio codec might not be compatible with `.m4a` container
- Copy mode fails, triggers automatic fallback to MP3

**Example**:
```
New video: MP4 with AAC audio → Copy to .m4a ✓ Works
Old video: MP4 with MP3 audio → Copy to .m4a ✗ Fails → Fallback to MP3 ✓ Works
```

## Automatic Fallback Strategy

### Step 1: Try Original Mode

First attempts extraction with configured mode:
- `copy`: Copy audio stream without re-encoding (fastest, best quality)
- `mp3_best`: MP3 VBR quality 0
- `mp3_high`: MP3 VBR quality 2
- `opus`: OPUS codec

### Step 2: Detect Failure

If extraction fails with error code -22 or 4294967274:
```
[01:22:47] [Thread-3] [4/598] Copy mode failed, trying re-encode...
```

### Step 3: Fallback to MP3

Automatically retries with MP3 encoding:
```python
# Fallback command
ffmpeg -y -i video.mp4 -vn -acodec libmp3lame -q:a 2 audio.mp3
```

### Step 4: Report Result

**Success**:
```
[01:22:48] [Thread-3] [4/598] ✓ Completed with fallback in 2.3s: audio.mp3
```

**Failure**:
```
[01:22:48] [Thread-3] [4/598] ⚠️  Failed: video.mp4 (error code: 4294967274)
```

## Pre-Extraction Checks

Before attempting extraction, the system checks:

### 1. File Already Exists (Any Format)
```
Status: skipped
Reason: already exists as .mp3
```
Skips extraction if audio file already present in **any format** (.mp3, .m4a, .opus, etc.).

**Why check all formats?**
- You may have changed `audio_extract_mode` between runs
- Old extractions might be in different format
- Prevents re-extracting audio that already exists

**Example**:
```
Old run: Extracted to .mp3 (mp3_best mode)
New run: Config changed to .m4a (copy mode)
Result: Skips extraction, uses existing .mp3 file
```

### 2. Video File Exists
```
Status: failed
Error: Video file not found
```
Fails if video file is missing.

### 3. Video File Not Empty
```
Status: failed
Error: Video file is empty (0 bytes)
```
Fails if video file is 0 bytes (corrupted/incomplete).

## Error Types

### Recoverable Errors

**Copy Mode Incompatibility**:
- Error: -22 or 4294967274
- Fallback: Re-encode to MP3
- Result: Audio extracted successfully

**Example**:
```
Video: H.265 codec with AAC audio
Copy mode: Fails (incompatible container)
Fallback: MP3 encoding succeeds
```

### Unrecoverable Errors

**No Audio Stream**:
- Video has no audio track
- Both copy and re-encode fail
- Result: Extraction fails

**Corrupted File**:
- Video file is damaged
- FFmpeg cannot read file
- Result: Extraction fails

**File System Issues**:
- Disk full
- Permission denied
- Path too long
- Result: Extraction fails

## Configuration

### Audio Extract Mode

Set in `config.json`:
```json
{
  "audio_extract_mode": "copy"
}
```

**Options**:
- `"copy"`: Fastest, best quality, but may fail on some files
- `"mp3_best"`: Slower, always works, excellent quality
- `"mp3_high"`: Good balance of speed and quality
- `"opus"`: YouTube's native format, excellent quality

**Recommendation**:
- Use `"copy"` for speed (automatic fallback handles failures)
- Use `"mp3_best"` if you want consistency

### Parallel Workers

Set in `config.json`:
```json
{
  "max_extraction_workers": 4
}
```

More workers = faster extraction, but more CPU usage.

## Format Change Handling

### Scenario: Changed audio_extract_mode

**What happens when you change extraction format?**

**Before**:
```json
{
  "audio_extract_mode": "mp3_best"
}
```
Result: All audio files are `.mp3`

**After**:
```json
{
  "audio_extract_mode": "copy"
}
```
Result: New extractions would be `.m4a`

**Problem**: Would the system re-extract all old MP3 files to M4A?

**Solution**: No! The system checks for audio in **any format**:
- Finds existing `.mp3` files
- Skips extraction
- Logs: `"already exists as .mp3"`
- No wasted processing

**Supported formats checked**:
- `.mp3` (MP3 encoding)
- `.m4a` (AAC in M4A container)
- `.opus` (Opus codec)
- `.mka` (Matroska audio)
- `.aac` (Raw AAC)
- `.ogg` (Ogg Vorbis)

### When Audio Gets Re-Extracted

Audio is only re-extracted if:
1. No audio file exists in any format
2. You manually delete the audio file
3. You move audio files to different location

## Troubleshooting

### Problem: Many Extraction Failures

**Symptoms**:
```
⚠️  Failed: video1.mp4 (error code: 4294967274)
⚠️  Failed: video2.mp4 (error code: 4294967274)
⚠️  Failed: video3.mp4 (error code: 4294967274)
```

**Possible Causes**:
1. Videos have no audio
2. FFmpeg not installed correctly
3. Corrupted downloads

**Solutions**:

**Check if videos have audio**:
```bash
ffmpeg -i video.mp4
```
Look for "Audio:" in output.

**Verify FFmpeg installation**:
```bash
ffmpeg -version
```
Should show version info.

**Re-download problematic videos**:
1. Remove from archive.txt
2. Delete video file
3. Download again

### Problem: Fallback Always Triggered

**Symptoms**:
```
Copy mode failed, trying re-encode...
Copy mode failed, trying re-encode...
Copy mode failed, trying re-encode...
```

**Cause**: Audio codec incompatible with copy mode

**Solution**: Change audio_extract_mode to `"mp3_best"`:
```json
{
  "audio_extract_mode": "mp3_best"
}
```

This skips copy mode entirely and always re-encodes.

### Problem: Extraction Very Slow

**Symptoms**: Taking hours for large playlists

**Causes**:
1. Re-encoding (slower than copy)
2. Too few parallel workers
3. Slow disk

**Solutions**:

**Increase parallel workers**:
```json
{
  "max_extraction_workers": 8
}
```

**Use copy mode** (if compatible):
```json
{
  "audio_extract_mode": "copy"
}
```

**Use faster codec**:
```json
{
  "audio_extract_mode": "opus"
}
```

### Problem: Audio Quality Poor

**Cause**: Using `"mp3_high"` or fallback mode

**Solution**: Use `"mp3_best"` or `"copy"`:
```json
{
  "audio_extract_mode": "mp3_best"
}
```

## Logging

### Success
```
[01:22:47] [Thread-3] [4/598] Extracting (copy): video.mp4
[01:22:48] [Thread-3] [4/598] ✓ Completed in 1.2s: audio.m4a
```

### Fallback Success
```
[01:22:47] [Thread-3] [4/598] Extracting (copy): video.mp4
[01:22:47] [Thread-3] [4/598] Copy mode failed, trying re-encode...
[01:22:49] [Thread-3] [4/598] ✓ Completed with fallback in 2.3s: audio.mp3
```

### Failure
```
[01:22:47] [Thread-3] [4/598] Extracting (copy): video.mp4
[01:22:47] [Thread-3] [4/598] Copy mode failed, trying re-encode...
[01:22:48] [Thread-3] [4/598] ⚠️  Failed: video.mp4 (error code: 4294967274)
```

## Summary Statistics

At the end of extraction:
```
Audio extraction summary:
  Total processed: 598/598
  Newly extracted: 595
  Skipped (already exist): 0
  Failed: 3
  Time taken: 245.3 seconds
  Average: 0.4 sec/file
```

## Best Practices

### 1. Use Copy Mode with Fallback

**Config**:
```json
{
  "audio_extract_mode": "copy"
}
```

**Benefits**:
- Fast for compatible files
- Automatic fallback for problematic files
- Best of both worlds

### 2. Adjust Workers Based on CPU

**4-core CPU**: 4 workers
**8-core CPU**: 6-8 workers
**16-core CPU**: 10-12 workers

Don't use all cores - leave some for system.

### 3. Monitor First Run

Watch the logs during first extraction:
- Many fallbacks? Consider changing mode
- Many failures? Check video files
- Very slow? Increase workers

### 4. Handle Failed Extractions

For videos that fail extraction:
1. Check if video has audio (play it)
2. Try manual extraction with FFmpeg
3. If no audio, exclude from playlist
4. If corrupted, re-download

## See Also

- [Audio/Video Quality Guide](AUDIO_VIDEO_QUALITY_GUIDE.md) - Quality settings
- [Parallel Operations](PARALLEL_OPERATIONS.md) - Concurrent extraction
- [Error Classification](ERROR_CLASSIFICATION.md) - Error types
