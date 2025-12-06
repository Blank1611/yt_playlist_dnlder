# View Modes - Grid and List

## Overview

The UI now supports two view modes for displaying playlists: Grid View and List View. Users can toggle between them based on their preference.

## Features

### 1. Grid View (Default) ✅
- **Card-based layout** - Each playlist in a card
- **3-column grid** on large screens
- **2-column grid** on medium screens
- **1-column** on mobile
- **All actions visible** - Buttons always shown
- **Visual stats** - Color-coded statistics

### 2. List View ✅
- **Table layout** - Compact rows
- **Expandable rows** - Click to show actions
- **More playlists visible** - See more at once
- **Quick overview** - Status badges
- **Efficient** - Better for many playlists

### 3. View Toggle ✅
- **Persistent** - Saves preference to localStorage
- **Easy switching** - Toggle buttons in header
- **Visual feedback** - Active view highlighted

## Usage

### Switching Views

1. Look for the view toggle buttons in the header (next to Settings)
2. Click the **Grid** icon (⊞) for grid view
3. Click the **List** icon (☰) for list view
4. Your preference is automatically saved

### Grid View

**Best for:**
- Visual browsing
- Seeing all details at once
- Quick access to all buttons
- Fewer playlists (< 10)

**Features:**
- All information visible
- All buttons accessible
- Progress bars always shown
- Color-coded cards

### List View

**Best for:**
- Many playlists (> 10)
- Quick scanning
- Compact display
- Efficient space usage

**Features:**
- Expandable rows
- Status badges
- Click row to expand/collapse
- Actions hidden until expanded

## UI Components

### View Toggle Buttons

Located in header, next to Settings:

```tsx
<div className="flex gap-1 p-1 rounded-lg bg-gray-200">
  <button onClick={() => setViewMode('grid')}>
    <Grid3x3 /> {/* Grid icon */}
  </button>
  <button onClick={() => setViewMode('list')}>
    <List /> {/* List icon */}
  </button>
</div>
```

**Active state:**
- White background (light mode)
- Blue text color
- Darker background (dark mode)

### Grid View Layout

```
┌─────────────┬─────────────┬─────────────┐
│  Playlist 1 │  Playlist 2 │  Playlist 3 │
│  ┌────────┐ │  ┌────────┐ │  ┌────────┐ │
│  │ Stats  │ │  │ Stats  │ │  │ Stats  │ │
│  └────────┘ │  └────────┘ │  └────────┘ │
│  [Buttons]  │  [Buttons]  │  [Buttons]  │
└─────────────┴─────────────┴─────────────┘
```

### List View Layout

```
┌──────────────────────────────────────────────────────┐
│ ▶ Playlist 1    │ 10 │ 15 │ 2 │ Pending            │
├──────────────────────────────────────────────────────┤
│ ▼ Playlist 2    │ 20 │ 20 │ 0 │ Complete           │
│   ┌────────────────────────────────────────────────┐ │
│   │ Progress Bars                                  │ │
│   │ [Download & Extract] [Download] [Extract]     │ │
│   │ [Refresh] [Edit Exclusions] [Remove]          │ │
│   └────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────┤
│ ▶ Playlist 3    │ 5  │ 10 │ 1 │ Pending            │
└──────────────────────────────────────────────────────┘
```

## List View Details

### Table Columns

| Column | Description | Width |
|--------|-------------|-------|
| ▶/▼ | Expand/collapse toggle | Fixed (48px) |
| Playlist | Title and status | Flexible |
| Local | Downloaded count | Fixed (80px) |
| Available | YouTube count | Fixed (80px) |
| Unavailable | Unavailable count | Fixed (100px) |
| Status | Badge (Running/Complete/Pending) | Fixed (100px) |

### Row States

**Collapsed (Default):**
- Shows basic info only
- Click anywhere to expand
- Chevron points right (▶)

**Expanded:**
- Shows progress bars (if running)
- Shows all action buttons
- Shows metadata (last download/extract)
- Chevron points down (▼)

### Status Badges

**Running:**
- Blue badge
- Shows when job is active
- Displays in Status column

**Complete:**
- Green badge
- Shows when caught up
- All videos downloaded

**Pending:**
- Gray badge
- Shows when videos need downloading
- Default state

### Expandable Content

When row is expanded, shows:

1. **Progress Bars** (if job running)
   - Download progress
   - Extraction progress
   - Batch information
   - View Logs button

2. **Action Buttons**
   - Download & Extract
   - Download
   - Extract
   - Refresh
   - Edit Exclusions (if any)
   - Remove

3. **Metadata**
   - Last download time
   - Last extract time

## Technical Implementation

### State Management

```typescript
const [viewMode, setViewMode] = useState<'grid' | 'list'>(() => {
  const saved = localStorage.getItem('viewMode')
  return (saved as 'grid' | 'list') || 'grid'
})

const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set())
```

### Persistence

```typescript
useEffect(() => {
  localStorage.setItem('viewMode', viewMode)
}, [viewMode])
```

View preference is saved to localStorage and restored on page load.

### Row Toggle

```typescript
const toggleRow = (playlistId: number) => {
  const newExpanded = new Set(expandedRows)
  if (newExpanded.has(playlistId)) {
    newExpanded.delete(playlistId)
  } else {
    newExpanded.add(playlistId)
  }
  setExpandedRows(newExpanded)
}
```

### Conditional Rendering

```typescript
{viewMode === 'grid' ? (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {/* Grid cards */}
  </div>
) : (
  <table className="w-full">
    {/* List rows */}
  </table>
)}
```

## Styling

### Grid View
- Cards with shadow
- Hover effect (shadow-lg)
- Green background for caught-up playlists
- Responsive grid columns

### List View
- Table with borders
- Hover effect on rows
- Alternating row colors (via divide-y)
- Green background for caught-up rows
- Expanded content with gray background

### Dark Mode Support
- Both views fully support dark mode
- Appropriate colors for all states
- Readable text in both modes

## Keyboard Shortcuts (Future)

Potential enhancements:
- [ ] Arrow keys to navigate rows
- [ ] Enter to expand/collapse
- [ ] Space to toggle selection
- [ ] G for grid view
- [ ] L for list view

## Benefits

### For Users
✅ **Choice** - Pick preferred view  
✅ **Efficiency** - List view for many playlists  
✅ **Visual** - Grid view for detailed overview  
✅ **Persistent** - Preference remembered  

### For Usability
✅ **Scalable** - List view handles many playlists  
✅ **Accessible** - Click anywhere to expand  
✅ **Responsive** - Works on all screen sizes  
✅ **Intuitive** - Clear visual feedback  

## Examples

### Grid View - 3 Playlists

```
┌─────────────────────────────────────────────────────────┐
│ My Music                                    ✓ Caught up │
│ ┌─────────┬─────────┬─────────┐                        │
│ │ 10      │ 10      │ 0       │                        │
│ │ Local   │ YouTube │ Unavail │                        │
│ └─────────┴─────────┴─────────┘                        │
│ [Download & Extract] [Download] [Extract]              │
│ [Refresh] [Remove]                                      │
└─────────────────────────────────────────────────────────┘
```

### List View - Collapsed

```
┌──────────────────────────────────────────────────────────┐
│ ▶ │ My Music              │ 10 │ 10 │ 0 │ Complete      │
│ ▶ │ Workout Mix           │ 5  │ 8  │ 1 │ Pending       │
│ ▶ │ Study Playlist        │ 20 │ 20 │ 0 │ Complete      │
│ ▶ │ Party Hits            │ 0  │ 15 │ 2 │ Pending       │
└──────────────────────────────────────────────────────────┘
```

### List View - Expanded

```
┌──────────────────────────────────────────────────────────┐
│ ▼ │ Workout Mix           │ 5  │ 8  │ 1 │ Running       │
│   │ 📥 Downloading 3/5                                   │
│   │ ████████░░░░░░░░░░░░░░░░░░░░                        │
│   │ 15/100 total (85 remaining)                          │
│   │                                                       │
│   │ [Cancel Job]                                         │
│   │ [View Logs]                                          │
│   │                                                       │
│   │ Last download: 2024-12-07 10:30:15                   │
└──────────────────────────────────────────────────────────┘
```

## Troubleshooting

### View Not Switching

**Check:**
1. Buttons are clickable
2. No JavaScript errors in console
3. localStorage is enabled

### Expanded State Not Saving

**Note:** Expanded state is intentionally not persisted. It resets on page reload to keep the list clean.

### Grid Too Crowded

**Solution:** Switch to list view for better space efficiency.

### List Too Compact

**Solution:** Switch to grid view for more visual detail.

## Future Enhancements

Potential improvements:
- [ ] Compact list view (even smaller rows)
- [ ] Column sorting (by name, count, status)
- [ ] Column filtering
- [ ] Bulk actions (select multiple)
- [ ] Drag-and-drop reordering
- [ ] Custom column visibility
- [ ] Export to CSV

## Related Files

- `yt_serve/frontend/src/App.tsx` - View mode implementation
- Icons from `lucide-react`: Grid3x3, List, ChevronDown, ChevronRight

---

**Implemented:** December 2024  
**Features:** Grid view, list view, expandable rows, persistent preference  
**Status:** ✅ Complete and ready to use
