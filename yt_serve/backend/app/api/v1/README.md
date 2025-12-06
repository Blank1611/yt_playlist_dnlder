# API v1

Version 1 of the API endpoints.

## Structure

```
v1/
├── endpoints/          # Individual endpoint modules
│   ├── playlists.py   # Playlist endpoints
│   ├── downloads.py   # Download endpoints
│   ├── config.py      # Config endpoints
│   └── websocket.py   # WebSocket endpoints
├── router.py          # Main v1 router
└── __init__.py
```

## Usage

All v1 endpoints are prefixed with `/api/v1/`:

- `/api/v1/playlists` - Playlist management
- `/api/v1/downloads` - Download operations
- `/api/v1/config` - Configuration
- `/api/v1/ws` - WebSocket connections

## Adding New Endpoints

1. Create new file in `endpoints/`
2. Define router and endpoints
3. Add to `router.py`
4. Update `endpoints/__init__.py`
