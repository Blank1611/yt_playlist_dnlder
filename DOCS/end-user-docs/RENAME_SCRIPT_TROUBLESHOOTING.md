# Rename Script Troubleshooting Guide

## Enhanced Features

The script now includes:
1. **Common pattern removal** - Removes "Official Video", "Lyric Video", etc.
2. **Artist separator normalization** - Treats `-`, `—`, `&` as spaces
3. **Partial title matching** - Finds 80% of title in filename
4. **Similar title suggestions** - Shows closest matches for unmatched files

## Understanding Unmatched Files

When files can't be matched, the script now shows similar titles from the playlist to help you understand why.

### Example Output

```
⚠️  3 files could not be matched:

   File: RADWIMPS - すずめ feat.十明 [Official Lyric Video].mp4
   Normalized: radwimpsすすめfeat十明officiallyricvideo...
   Most similar titles in playlist:
     - すずめ (feat. 十明) (similarity: 75%)
       Normalized: すすめfeat十明...
       ID: abc123xyz
     - RADWIMPS - すずめ (similarity: 65%)
       Normalized: radwimpsすすめ...
       ID: def456uvw
```

## Common Patterns Removed

The script automatically removes these patterns before matching:
- `official video`
- `official lyric video`
- `official music video`
- `official audio`
- `lyric video`
- `music video`
- `official mv`
- `official`
- `hd`, `4k`, `1080p`, `720p`
- `full video`, `full song`
- `video song`
- `audio`, `lyrics`
- `feat`, `ft`, `featuring`

## Artist Separators Normalized

These are all treated as spaces:
- `-` (hyphen)
- `—` (em dash)
- `–` (en dash)
- `&` (ampersand)
- `|` (pipe)
- `/` (forward slash)
- `\` (backslash)

## Manual Matching for Unmatched Files

If the script shows similar titles but doesn't match automatically, you can:

### Option 1: Manual Rename
```bash
# Use the ID from the similar titles output
mv "RADWIMPS - すずめ feat.十明 [Official Lyric Video].mp4" "RADWIMPS - すずめ feat.十明 [abc123xyz].mp4"
```

### Option 2: Lower Match Threshold

Edit the script and change:
```python
if matched_id and best_score >= 65:  # Lower to 60 or 55
```

### Option 3: Add Custom Pattern

If your files have a specific pattern, add it to `remove_common_patterns()`:
```python
patterns_to_remove = [
    # ... existing patterns ...
    'your custom pattern',
]
```

## Why Files Don't Match

### Case 1: Title Format Difference
```
Filename: "Artist - Song [Official Video]"
Title:    "Song (feat. Artist)"

Problem: Word order completely different
Solution: Manual rename using suggested ID
```

### Case 2: Extra Information in Filename
```
Filename: "Song Title (Extended Mix) [Official Audio]"
Title:    "Song Title"

Problem: "(Extended Mix)" not in original title
Solution: Script should match after removing patterns
         If not, check if pattern is in removal list
```

### Case 3: Different Language/Script
```
Filename: "Song Title (Romanized)"
Title:    "गाना शीर्षक" (Original script)

Problem: Completely different scripts
Solution: Manual rename - no automatic matching possible
```

### Case 4: Abbreviated Artist Names
```
Filename: "R&F - Song"
Title:    "Rauf & Faik - Song"

Problem: Abbreviated vs full name
Solution: May match with partial matching (65% threshold)
```

## Debugging Steps

### 1. Check Normalized Versions
Look at the normalized output:
```
Normalized filename: radwimpsすすめfeat十明officiallyricvideo
Normalized title:    すすめfeat十明
```

If they're very different, matching won't work.

### 2. Check Similar Titles
The script shows the 3 most similar titles. If similarity is:
- **>80%**: Should match automatically (check threshold)
- **60-80%**: May need to lower threshold
- **<60%**: Probably need manual rename

### 3. Verify playlist_info.json
Make sure the title in playlist_info.json matches what you expect:
```bash
# Search for a specific video ID
grep "abc123xyz" playlist_info_snapshot/playlist_info.json
```

### 4. Check archive.txt
Verify the video ID is in archive.txt:
```bash
grep "abc123xyz" archive.txt
```

## Advanced Solutions

### Batch Manual Rename

Create a mapping file `manual_renames.txt`:
```
RADWIMPS - すずめ feat.十明 [Official Lyric Video].mp4|abc123xyz
Rauf & Faik — детство (Official video).mp4|def456uvw
Rauf Faik - вечера (Official video).mp4|ghi789rst
```

Then use a script to apply:
```python
with open('manual_renames.txt', 'r', encoding='utf-8') as f:
    for line in f:
        old_name, vid_id = line.strip().split('|')
        name_without_ext = os.path.splitext(old_name)[0]
        new_name = f"{name_without_ext} [{vid_id}].mp4"
        os.rename(old_name, new_name)
```

### Custom Matching Function

Add your own matching logic:
```python
# In the matching loop, add:
elif custom_match_logic(normalized_filename, norm_title):
    score = 85
    match_type = "custom match"
```

## See Also

- [Rename Script Guide](RENAME_SCRIPT_GUIDE.md) - Main documentation
- [Old Format Auto-Rename](OLD_FORMAT_AUTO_RENAME.md) - Automatic renaming in main app
