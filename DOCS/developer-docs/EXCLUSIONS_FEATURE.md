# Edit Exclusions Feature

## Overview

The Edit Exclusions feature allows you to manage which videos are excluded from downloads, matching the functionality from the Tkinter version.

## How to Access

### From Playlist Card

When a playlist has excluded videos, you'll see:
```
31 videos excluded [Edit]
```

Click the "Edit" button to open the exclusions editor.

## Exclusions Modal

### Layout

```
┌─────────────────────────────────────────────┐
│ Edit Exclusions: Awesome                 ✕  │
│ Excluded videos will be skipped during      │
│ downloads                                   │
├─────────────────────────────────────────────┤
│                                             │
│ Add Video ID to Exclude                     │
│ [dQw4w9WgXcQ                    ] [Add]     │
│                                             │
│ Excluded Video IDs (31)                     │
│ ┌─────────────────────────────────────────┐ │
│ │ 2ZBbEKKAGHw  View on YouTube      [×]   │ │
│ │ 3FygIKsnkCw  View on YouTube      [×]   │ │
│ │ 4zddJkI7UDM  View on YouTube      [×]   │ │
│ │ ...                                     │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ [Save Changes] [Cancel]                     │
└─────────────────────────────────────────────┘
```

## Features

### 1. Add Video ID

**Input Field:**
- Enter YouTube video ID
- Example: `dQw4w9WgXcQ`
- Press Enter or click "Add"

**Validation:**
- Trims whitespace
- Prevents duplicates
- Requires non-empty input

### 2. View Excluded Videos

**List Display:**
- Shows all excluded video IDs
- Scrollable if many exclusions
- Each entry shows:
  - Video ID (monospace font)
  - "View on YouTube" link
  - Remove button (×)

**Empty State:**
- Shows "No videos excluded" when list is empty

### 3. Remove Exclusions

**Remove Button:**
- Click × to remove from exclusions
- Immediate visual feedback
- Changes not saved until "Save Changes"

### 4. View on YouTube

**Link:**
- Opens video in new tab
- Format: `https://www.youtube.com/watch?v={id}`
- Verify which video is excluded

### 5. Save Changes

**Save Button:**
- Updates playlist exclusions
- Shows loading state
- Success alert on completion
- Closes modal automatically

## Use Cases

### 1. Exclude Unavailable Videos

Videos that are:
- Deleted
- Private
- Region-blocked
- Copyright claimed

**Workflow:**
1. Download fails for video
2. Check logs for video ID
3. Open Edit Exclusions
4. Add video ID
5. Save
6. Re-run download (skips excluded)

### 2. Exclude Unwanted Content

Videos you don't want:
- Duplicates
- Wrong language
- Inappropriate content
- Low quality

**Workflow:**
1. Identify video ID from YouTube
2. Open Edit Exclusions
3. Add video ID
4. Save
5. Future downloads skip it

### 3. Remove Old Exclusions

Videos that are now available:
- Previously private, now public
- Copyright resolved
- Want to download now

**Workflow:**
1. Open Edit Exclusions
2. Find video ID in list
3. Click × to remove
4. Save
5. Next download includes it

### 4. Bulk Management

Manage many exclusions:
- View all at once
- Add multiple IDs
- Remove multiple IDs
- Save all changes together

## Technical Details

### Video ID Format

**YouTube Video ID:**
- 11 characters
- Alphanumeric + `-` and `_`
- Example: `dQw4w9WgXcQ`

**Where to Find:**
- URL: `youtube.com/watch?v=dQw4w9WgXcQ`
- Share link: `youtu.be/dQw4w9WgXcQ`
- Logs: `Failed to download: dQw4w9WgXcQ`

### State Management

```typescript
const [excludedIds, setExcludedIds] = useState<string[]>(
  playlist.excluded_ids || []
)
```

**Operations:**
- Add: `setExcludedIds([...excludedIds, newId])`
- Remove: `setExcludedIds(excludedIds.filter(id => id !== removeId))`
- Save: `playlistsApi.update(playlist.id, { excluded_ids: excludedIds })`

### API Integration

**Update Endpoint:**
```typescript
PUT /api/playlists/{id}
{
  "excluded_ids": ["id1", "id2", "id3"]
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Awesome",
  "excluded_ids": ["id1", "id2", "id3"],
  ...
}
```

## Visual Design

### Modal Styling

**Colors:**
- Background: White / Dark Gray
- Border: Gray
- Buttons: Blue (primary), Gray (secondary), Red (remove)

**Layout:**
- Header: Fixed at top
- Content: Scrollable
- Footer: Fixed at bottom

### List Items

**Each Exclusion:**
```
┌─────────────────────────────────────────┐
│ dQw4w9WgXcQ  View on YouTube      [×]   │
└─────────────────────────────────────────┘
```

**Hover States:**
- Background lightens
- Remove button highlights
- Link underlines

### Responsive Design

**Desktop:**
- Modal: 600px wide
- List: Scrollable at 384px height

**Mobile:**
- Modal: Full width with padding
- List: Scrollable
- Touch-friendly buttons

## Keyboard Shortcuts

**In Add Field:**
- `Enter` - Add video ID
- `Escape` - Close modal (if focused)

**In Modal:**
- `Escape` - Close modal
- `Tab` - Navigate fields

## Error Handling

### Duplicate ID

**Behavior:**
- Silently ignores
- No error message
- Input field clears

**Why:**
- User might not remember if already added
- Non-destructive
- Simple UX

### Empty Input

**Behavior:**
- Add button disabled
- No action on Enter
- Visual feedback (gray button)

### Save Failure

**Behavior:**
- Error alert shown
- Modal stays open
- Changes preserved
- User can retry

## Comparison with Tkinter

| Feature | Tkinter | Web UI |
|---------|---------|--------|
| Add exclusion | ✅ Yes | ✅ Yes |
| Remove exclusion | ✅ Yes | ✅ Yes |
| View list | ✅ Yes | ✅ Yes |
| View on YouTube | ❌ No | ✅ Yes |
| Search/filter | ❌ No | ⚠️ Future |
| Bulk operations | ⚠️ Limited | ⚠️ Future |
| Visual design | ⚠️ Basic | ✅ Modern |

## Future Enhancements

### Possible Additions

1. **Search/Filter**
   - Search by video ID
   - Filter by date added
   - Sort alphabetically

2. **Bulk Operations**
   - Select multiple
   - Remove selected
   - Import from file
   - Export to file

3. **Video Metadata**
   - Show video title
   - Show thumbnail
   - Show reason for exclusion
   - Show date added

4. **Smart Suggestions**
   - Auto-detect failed videos
   - Suggest exclusions
   - One-click add from logs

5. **Undo/Redo**
   - Undo last removal
   - Redo last addition
   - Change history

## Best Practices

### For Users

**When to Exclude:**
- Video permanently unavailable
- Don't want specific content
- Duplicate videos
- Wrong language/region

**When NOT to Exclude:**
- Temporary network errors
- Transient YouTube issues
- First download attempt

**Workflow:**
1. Try download first
2. Check logs for failures
3. Verify video is truly unavailable
4. Add to exclusions
5. Re-run download

### For Developers

**State Management:**
- Keep local state until save
- Don't mutate props
- Validate before save
- Handle errors gracefully

**UX Considerations:**
- Confirm before removing
- Show loading states
- Provide feedback
- Make links obvious

## Summary

The Edit Exclusions feature provides:

✅ **Easy Management** - Add/remove exclusions visually  
✅ **View on YouTube** - Verify which videos are excluded  
✅ **Bulk Editing** - Manage all exclusions at once  
✅ **Modern UI** - Clean, intuitive interface  
✅ **Tkinter Parity** - Matches original functionality  

This feature helps users manage problematic videos and customize their downloads effectively!
