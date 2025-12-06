# Backend Structure

## Overview

The backend has been organized following FastAPI best practices for better maintainability, scalability, and testability.

## Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   │
│   ├── core/                   # Core configuration and utilities
│   │   ├── __init__.py
│   │   ├── config.py          # Pydantic settings
│   │   └── yt_playlist_audio_tools.py  # Core download logic
│   │
│   ├── models/                 # Database models (SQLAlchemy)
│   │   ├── __init__.py
│   │   └── database.py        # Database setup and models
│   │
│   ├── schemas/                # Pydantic schemas (NEW)
│   │   ├── __init__.py
│   │   ├── example.py         # Example schemas
│   │   └── README.md
│   │
│   ├── api/                    # API route handlers
│   │   ├── __init__.py
│   │   ├── v1/                # API Version 1 (NEW)
│   │   │   ├── __init__.py
│   │   │   ├── router.py      # Main v1 router
│   │   │   ├── README.md
│   │   │   └── endpoints/     # Individual endpoints
│   │   │       ├── __init__.py
│   │   │       ├── playlists.py
│   │   │       ├── downloads.py
│   │   │       ├── config.py
│   │   │       └── websocket.py
│   │   │
│   │   └── (old files - can be removed after migration)
│   │
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── job_manager.py     # Job management service
│   │   └── ytdlp_service.py   # YouTube download service
│   │
│   └── utils/                  # Helper functions (NEW)
│       ├── __init__.py
│       ├── example.py         # Example utilities
│       └── README.md
│
├── tests/                      # Pytest test suite (NEW)
│   ├── __init__.py
│   ├── conftest.py            # Pytest fixtures
│   ├── test_example.py        # Example tests
│   └── README.md
│
├── .env                        # Environment variables (git-ignored)
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
├── run.py                      # Application runner
└── BACKEND_STRUCTURE.md        # This file
```

## Design Principles

### 1. Layered Architecture

```
API Layer (api/)
    ↓
Service Layer (services/)
    ↓
Data Layer (models/)
```

- **API Layer**: Handles HTTP requests/responses
- **Service Layer**: Contains business logic
- **Data Layer**: Database operations

### 2. Separation of Concerns

Each directory has a specific responsibility:
- **core/**: Configuration and core utilities
- **models/**: Database models and schemas
- **schemas/**: Request/response validation
- **api/**: HTTP endpoint handlers
- **services/**: Business logic
- **utils/**: Helper functions

### 3. API Versioning

Using `/api/v1/` prefix for all endpoints:
- Easy to add v2 without breaking v1
- Clear API evolution path
- Better client compatibility

## File Organization

### Core (`app/core/`)

**Purpose:** Core configuration and utilities

**Files:**
- `config.py` - Pydantic settings (from .env)
- `yt_playlist_audio_tools.py` - Core download logic

**Usage:**
```python
from app.core.config import settings
from app.core import yt_playlist_audio_tools
```

### Models (`app/models/`)

**Purpose:** Database models and ORM setup

**Files:**
- `database.py` - SQLAlchemy models and database setup

**Usage:**
```python
from app.models.database import Playlist, Job, get_db
```

### Schemas (`app/schemas/`)

**Purpose:** Pydantic models for request/response validation

**Structure:**
```python
# schemas/playlist.py
class PlaylistCreate(BaseModel):
    url: str

class PlaylistResponse(BaseModel):
    id: int
    url: str
    title: str
    # ...
```

**Usage:**
```python
from app.schemas import PlaylistCreate, PlaylistResponse

@router.post("/", response_model=PlaylistResponse)
async def create_playlist(playlist: PlaylistCreate):
    # ...
```

### API (`app/api/`)

**Purpose:** HTTP endpoint handlers

**Structure:**
```
api/
├── v1/
│   ├── router.py          # Aggregates all v1 endpoints
│   └── endpoints/
│       ├── playlists.py   # Playlist CRUD
│       ├── downloads.py   # Download operations
│       ├── config.py      # Configuration
│       └── websocket.py   # WebSocket connections
```

**Usage:**
```python
# In main.py
from app.api.v1.router import router as v1_router
app.include_router(v1_router, prefix="/api/v1")
```

### Services (`app/services/`)

**Purpose:** Business logic layer

**Files:**
- `job_manager.py` - Job queue and management
- `ytdlp_service.py` - YouTube download operations

**Usage:**
```python
from app.services.ytdlp_service import DownloadService

service = DownloadService(base_path, config)
await service.download_playlist(url, excluded_ids)
```

### Utils (`app/utils/`)

**Purpose:** Helper functions and utilities

**Examples:**
```python
# utils/file_helpers.py
def sanitize_filename(name: str) -> str:
    # Remove invalid characters
    pass

# utils/validators.py
def is_valid_youtube_url(url: str) -> bool:
    # Validate YouTube URL
    pass
```

**Usage:**
```python
from app.utils import sanitize_filename, is_valid_youtube_url
```

### Tests (`tests/`)

**Purpose:** Automated testing with pytest

**Structure:**
```
tests/
├── conftest.py         # Shared fixtures
├── test_api/          # API endpoint tests
├── test_services/     # Service layer tests
└── test_utils/        # Utility function tests
```

**Usage:**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test
pytest tests/test_api/test_playlists.py
```

## API Versioning

### Current Structure

All endpoints are under `/api/v1/`:

```
/api/v1/playlists       # Playlist management
/api/v1/downloads       # Download operations
/api/v1/config          # Configuration
/api/v1/ws              # WebSocket
```

### Adding New Endpoints

1. Create file in `app/api/v1/endpoints/`:
```python
# app/api/v1/endpoints/new_feature.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_items():
    return {"items": []}
```

2. Add to `app/api/v1/router.py`:
```python
from app.api.v1.endpoints import new_feature

router.include_router(
    new_feature.router,
    prefix="/new-feature",
    tags=["new-feature"]
)
```

### Future: API v2

When needed, create `app/api/v2/`:
```python
# main.py
from app.api.v1.router import router as v1_router
from app.api.v2.router import router as v2_router

app.include_router(v1_router, prefix="/api/v1")
app.include_router(v2_router, prefix="/api/v2")
```

## Configuration

### Environment Variables

Managed through `.env` file:

```env
# Database
DATABASE_URL=sqlite:///./yt_manager.db

# Download Settings
BASE_DOWNLOAD_PATH=downloads
MAX_CONCURRENT_EXTRACTIONS=4

# API Settings
API_V1_STR=/api/v1
PROJECT_NAME=YouTube Playlist Manager
```

### Pydantic Settings

Loaded in `app/core/config.py`:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./yt_manager.db"
    BASE_DOWNLOAD_PATH: str = "downloads"
    # ...
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## Testing

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/test_api/test_playlists.py

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Writing Tests

```python
# tests/test_api/test_playlists.py
def test_create_playlist(client):
    """Test creating a playlist"""
    response = client.post("/api/v1/playlists", json={
        "url": "https://youtube.com/playlist?list=..."
    })
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["url"] == "https://youtube.com/playlist?list=..."
```

### Fixtures

Common fixtures in `conftest.py`:

```python
@pytest.fixture
def client():
    """Test client fixture"""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def db():
    """Database session fixture"""
    # Setup test database
    yield db_session
    # Teardown
```

## Best Practices

### 1. Dependency Injection

```python
from fastapi import Depends
from app.models.database import get_db

@router.get("/")
async def list_playlists(db: Session = Depends(get_db)):
    playlists = db.query(Playlist).all()
    return playlists
```

### 2. Error Handling

```python
from fastapi import HTTPException

@router.get("/{id}")
async def get_playlist(id: int, db: Session = Depends(get_db)):
    playlist = db.query(Playlist).filter(Playlist.id == id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return playlist
```

### 3. Response Models

```python
from app.schemas import PlaylistResponse

@router.get("/", response_model=list[PlaylistResponse])
async def list_playlists(db: Session = Depends(get_db)):
    return db.query(Playlist).all()
```

### 4. Service Layer

```python
# In endpoint
@router.post("/")
async def create_playlist(
    playlist: PlaylistCreate,
    service: PlaylistService = Depends(get_playlist_service)
):
    return await service.create(playlist)

# In service
class PlaylistService:
    async def create(self, playlist: PlaylistCreate):
        # Business logic here
        pass
```

## Migration Guide

### Current State

- ✅ API endpoints copied to `v1/endpoints/`
- ✅ V1 router created
- ✅ Schemas directory created
- ✅ Utils directory created
- ✅ Tests directory created
- ⏳ Old API files still in `api/` (for compatibility)

### Next Steps

1. **Update main.py to use v1 router:**
```python
from app.api.v1.router import router as v1_router
app.include_router(v1_router, prefix="/api/v1")
```

2. **Create proper schemas:**
```python
# app/schemas/playlist.py
class PlaylistCreate(BaseModel):
    url: str

class PlaylistResponse(BaseModel):
    id: int
    url: str
    title: str
    # ...
```

3. **Add tests:**
```python
# tests/test_api/test_playlists.py
def test_list_playlists(client):
    response = client.get("/api/v1/playlists")
    assert response.status_code == 200
```

4. **Remove old API files** (after v1 is verified)

## Benefits

### Maintainability
✅ **Clear structure** - Easy to find and modify code  
✅ **Separation of concerns** - Each layer has one responsibility  
✅ **Testable** - Isolated components are easy to test  

### Scalability
✅ **API versioning** - Easy to add v2 without breaking v1  
✅ **Modular** - Add new features without affecting existing code  
✅ **Service layer** - Business logic separate from HTTP layer  

### Developer Experience
✅ **Type safety** - Pydantic schemas throughout  
✅ **Documentation** - README in each directory  
✅ **Testing** - Pytest setup with fixtures  

## Resources

- **[FastAPI Documentation](https://fastapi.tiangolo.com/)** - Official FastAPI docs
- **[Pydantic Documentation](https://docs.pydantic.dev/)** - Pydantic validation
- **[SQLAlchemy Documentation](https://docs.sqlalchemy.org/)** - Database ORM
- **[Pytest Documentation](https://docs.pytest.org/)** - Testing framework

## Questions?

See the README files in each directory:
- `app/schemas/README.md`
- `app/utils/README.md`
- `app/api/v1/README.md`
- `tests/README.md`

---

**Last Updated:** December 2024  
**Structure Version:** 2.0  
**Status:** ✅ Reorganized and ready for development
