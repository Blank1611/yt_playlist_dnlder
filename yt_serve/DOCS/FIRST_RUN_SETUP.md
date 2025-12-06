# First-Run Setup Feature

## Overview

The yt_serve web application now includes an automatic first-run setup wizard that guides users through initial configuration.

## How It Works

### 1. Detection

On startup, the backend checks if setup is needed by:
- Checking if `.env` file exists
- Verifying `BASE_DOWNLOAD_PATH` is set to a real path (not default "downloads")
- Confirming the download path exists

If any check fails, `needs_setup: true` is returned in the config API.

### 2. Setup Modal

When `needs_setup` is true, the frontend automatically shows an "Initial Setup" modal that:
- **Cannot be dismissed** until setup is complete
- Has a clear, user-friendly interface
- Highlights required fields
- Provides helpful hints and examples

### 3. Required Fields

**Mandatory:**
- **Download Directory** - Full path where playlists will be saved
  - Example: `E:\Music\YouTube`
  - Must be a valid, existing path

**Optional:**
- **Authentication** - For age-restricted or private videos
  - Use Browser Cookies (Chrome, Firefox, Edge, Safari)
  - OR Cookies File Path
- **Advanced Settings** (collapsed by default)
  - Audio Extract Mode
  - Max Concurrent Extractions
  - Batch Size

### 4. Persistence

When setup is completed:
- Settings are saved to `.env` file in `yt_serve/backend/`
- Settings are also updated in-memory
- `needs_setup` flag becomes `false`
- User can start using the app

## User Experience

### First Launch

```
1. User opens http://localhost:5173
2. App loads and checks config
3. "Initial Setup" modal appears automatically
4. User fills in download directory (required)
5. Optionally configures cookies/advanced settings
6. Clicks "Complete Setup"
7. Settings saved to .env
8. Modal closes, app is ready to use
```

### Subsequent Launches

```
1. User opens http://localhost:5173
2. App loads and checks config
3. needs_setup = false
4. App loads normally, no setup modal
```

## Technical Details

### Backend Changes

**File:** `yt_serve/backend/app/api/config.py`

**New Functions:**
```python
def _check_needs_setup() -> bool:
    """Check if initial setup is needed"""
    # Returns True if .env missing or BASE_DOWNLOAD_PATH is default/invalid

def _save_to_env(config: ConfigUpdate):
    """Save configuration to .env file"""
    # Persists settings to .env for permanent storage
```

**Updated Response:**
```python
class ConfigResponse(BaseModel):
    # ... existing fields ...
    needs_setup: bool  # NEW: Flag for first-run setup
```

### Frontend Changes

**File:** `yt_serve/frontend/src/App.tsx`

**New Component:**
```typescript
function InitialSetupModal({ onClose, onComplete })
```

**Features:**
- Auto-shows when `config.needs_setup === true`
- Cannot be dismissed (no X button, no click-outside)
- Required field validation
- Collapsible advanced settings
- Clear visual hierarchy (required fields highlighted)

**File:** `yt_serve/frontend/src/api.ts`

**Updated Interface:**
```typescript
export interface Config {
  // ... existing fields ...
  needs_setup: boolean  // NEW
}
```

## Configuration Flow

```
┌─────────────────────────────────────────────────────────┐
│ 1. App Starts                                           │
│    GET /api/config                                      │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 2. Backend Checks                                       │
│    - .env exists?                                       │
│    - BASE_DOWNLOAD_PATH set?                            │
│    - Path exists?                                       │
└────────────────┬────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
┌──────────────┐  ┌──────────────────┐
│ needs_setup  │  │ needs_setup      │
│ = false      │  │ = true           │
│              │  │                  │
│ Normal UI    │  │ Setup Modal      │
└──────────────┘  └────────┬─────────┘
                           │
                           ▼
                  ┌─────────────────────┐
                  │ 3. User Fills Form  │
                  │    - Download path  │
                  │    - Cookies (opt)  │
                  │    - Advanced (opt) │
                  └────────┬────────────┘
                           │
                           ▼
                  ┌─────────────────────┐
                  │ 4. Submit           │
                  │    PUT /api/config  │
                  └────────┬────────────┘
                           │
                           ▼
                  ┌─────────────────────┐
                  │ 5. Backend Saves    │
                  │    - Update memory  │
                  │    - Write to .env  │
                  └────────┬────────────┘
                           │
                           ▼
                  ┌─────────────────────┐
                  │ 6. Setup Complete   │
                  │    needs_setup=false│
                  │    Modal closes     │
                  │    App ready!       │
                  └─────────────────────┘
```

## Benefits

### For Users
✅ **No manual .env editing** - Everything done through UI  
✅ **Clear guidance** - Required fields highlighted  
✅ **Can't skip** - Ensures proper configuration  
✅ **Helpful hints** - Examples and descriptions provided  
✅ **Optional advanced** - Simple by default, powerful when needed  

### For Developers
✅ **Automatic detection** - No manual trigger needed  
✅ **Persistent storage** - Settings saved to .env  
✅ **Type-safe** - Pydantic validation  
✅ **Reusable** - Same form as Settings modal  

## Testing

### Test First-Run

1. Delete or rename `.env` file:
   ```bash
   cd yt_serve/backend
   del .env  # or rename .env .env.backup
   ```

2. Start the app:
   ```bash
   cd yt_serve
   LAUNCH_APP.bat
   ```

3. Open browser: http://localhost:5173

4. Setup modal should appear automatically

5. Fill in download directory and click "Complete Setup"

6. Check that `.env` was created with your settings

### Test Normal Launch

1. With `.env` configured, start the app

2. Setup modal should NOT appear

3. App loads normally

### Test Settings Change

1. Click Settings button (gear icon)

2. Change any setting

3. Save

4. Settings should persist to `.env`

5. Restart app - settings should be retained

## Customization

### Change Required Fields

Edit `_check_needs_setup()` in `yt_serve/backend/app/api/config.py`:

```python
def _check_needs_setup() -> bool:
    # Add more checks as needed
    if not settings.COOKIES_FILE:  # Make cookies required
        return True
    return False
```

### Change Modal Appearance

Edit `InitialSetupModal` in `yt_serve/frontend/src/App.tsx`:

```typescript
// Change title
<h2>Welcome to YouTube Playlist Manager!</h2>

// Add more fields
<div>
  <label>Your Custom Field</label>
  <input ... />
</div>
```

### Add Validation

In `handleSubmit()`:

```typescript
// Add custom validation
if (formData.batch_size < 50) {
  alert('Batch size must be at least 50')
  return
}
```

## Future Enhancements

Potential improvements:
- [ ] Path validation (check if directory exists)
- [ ] Create directory if it doesn't exist
- [ ] Test cookies file before saving
- [ ] Import settings from Tkinter version
- [ ] Multi-step wizard for complex setups
- [ ] Setup progress indicator
- [ ] Guided tour after setup

## Troubleshooting

### Setup modal keeps appearing

- Check that `.env` file was created in `yt_serve/backend/`
- Verify `BASE_DOWNLOAD_PATH` is set to a real path
- Ensure the path exists on your system

### Settings not persisting

- Check file permissions on `yt_serve/backend/.env`
- Verify backend has write access to the directory
- Check backend logs for errors

### Can't dismiss setup modal

- This is intentional! Complete the setup to proceed
- If you need to skip, manually create `.env` with required settings

## Related Files

- `yt_serve/backend/app/api/config.py` - Backend config API
- `yt_serve/frontend/src/App.tsx` - Frontend setup modal
- `yt_serve/frontend/src/api.ts` - API types
- `yt_serve/backend/.env` - Configuration file (created by setup)
- `yt_serve/backend/app/core/config.py` - Settings model
