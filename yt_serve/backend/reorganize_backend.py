"""
Reorganize backend structure according to best practices
"""
import shutil
from pathlib import Path

def reorganize_backend():
    print("="*60)
    print("Reorganizing Backend Structure")
    print("="*60)
    print()
    
    # Get the backend directory
    backend = Path(__file__).parent.resolve()
    app = backend / "app"
    
    print(f"Working directory: {backend}")
    print()
    
    # Create new directory structure
    directories = [
        "app/api/v1",
        "app/api/v1/endpoints",
        "app/schemas",
        "app/utils",
        "tests",
    ]
    
    print("Creating directory structure...")
    for dir_path in directories:
        full_path = backend / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {dir_path}/")
    
    print()
    print("Moving API endpoints to v1/endpoints/...")
    
    # Move API files to v1/endpoints/
    api_files = [
        "config.py",
        "downloads.py",
        "playlists.py",
        "websocket.py",
    ]
    
    api_dir = app / "api"
    v1_endpoints = app / "api" / "v1" / "endpoints"
    
    for file in api_files:
        src = api_dir / file
        dest = v1_endpoints / file
        if src.exists() and not dest.exists():
            shutil.copy2(str(src), str(dest))
            print(f"  ✓ {file} -> api/v1/endpoints/")
    
    print()
    print("Creating __init__.py files...")
    
    # Create __init__.py files
    init_files = [
        "app/api/v1/__init__.py",
        "app/api/v1/endpoints/__init__.py",
        "app/schemas/__init__.py",
        "app/utils/__init__.py",
        "tests/__init__.py",
    ]
    
    for init_file in init_files:
        init_path = backend / init_file
        if not init_path.exists():
            init_path.write_text("", encoding='utf-8')
            print(f"  ✓ {init_file}")
    
    print()
    print("Creating v1 router...")
    
    # Create v1 router
    v1_router = app / "api" / "v1" / "router.py"
    if not v1_router.exists():
        v1_router.write_text("""\"\"\"
API v1 Router - Aggregates all v1 endpoints
\"\"\"
from fastapi import APIRouter

from app.api.v1.endpoints import playlists, downloads, config, websocket

router = APIRouter()

# Include all endpoint routers
router.include_router(playlists.router, prefix="/playlists", tags=["playlists"])
router.include_router(downloads.router, prefix="/downloads", tags=["downloads"])
router.include_router(config.router, prefix="/config", tags=["config"])
router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
""", encoding='utf-8')
        print("  ✓ api/v1/router.py")
    
    # Update v1/endpoints/__init__.py
    v1_endpoints_init = app / "api" / "v1" / "endpoints" / "__init__.py"
    v1_endpoints_init.write_text("""\"\"\"
API v1 Endpoints
\"\"\"
from app.api.v1.endpoints import playlists, downloads, config, websocket

__all__ = ["playlists", "downloads", "config", "websocket"]
""", encoding='utf-8')
    print("  ✓ api/v1/endpoints/__init__.py (updated)")
    
    print()
    print("Creating README files...")
    
    readmes = {
        "app/schemas/README.md": """# Schemas

Pydantic schemas for request/response validation.

## Purpose

- Define API request models
- Define API response models
- Provide data validation
- Generate OpenAPI documentation

## Structure

```
schemas/
├── playlist.py      # Playlist-related schemas
├── job.py          # Job-related schemas
├── config.py       # Config-related schemas
└── __init__.py     # Export all schemas
```

## Usage

```python
from app.schemas import PlaylistCreate, PlaylistResponse

# In API endpoint:
@router.post("/", response_model=PlaylistResponse)
async def create_playlist(playlist: PlaylistCreate):
    # ...
```

## Best Practices

- Use Pydantic BaseModel for all schemas
- Separate Create, Update, and Response models
- Add field validation and descriptions
- Use Optional for nullable fields
""",
        "app/utils/README.md": """# Utils

Helper functions and utilities.

## Purpose

- Reusable utility functions
- Common helpers
- Formatting and validation
- File operations

## Examples

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

## Usage

```python
from app.utils import sanitize_filename, is_valid_youtube_url
```
""",
        "app/api/v1/README.md": """# API v1

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
""",
        "tests/README.md": """# Tests

Pytest test suite for the backend.

## Structure

```
tests/
├── conftest.py         # Pytest fixtures
├── test_api/          # API endpoint tests
├── test_services/     # Service layer tests
├── test_models/       # Database model tests
└── test_utils/        # Utility function tests
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_api/test_playlists.py

# Run with verbose output
pytest -v
```

## Writing Tests

```python
# tests/test_api/test_playlists.py
def test_create_playlist(client):
    response = client.post("/api/v1/playlists", json={
        "url": "https://youtube.com/playlist?list=..."
    })
    assert response.status_code == 200
```

## Fixtures

Common fixtures in `conftest.py`:
- `client` - TestClient for API testing
- `db` - Database session
- `mock_ytdlp` - Mocked yt-dlp service
""",
    }
    
    for path, content in readmes.items():
        readme_path = backend / path
        if not readme_path.exists():
            readme_path.write_text(content, encoding='utf-8')
            print(f"  ✓ {path}")
    
    print()
    print("Creating example files...")
    
    # Create example schema file
    example_schema = app / "schemas" / "example.py"
    if not example_schema.exists():
        example_schema.write_text("""\"\"\"
Example Pydantic schemas
\"\"\"
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Request schemas
class PlaylistCreate(BaseModel):
    \"\"\"Schema for creating a playlist\"\"\"
    url: str = Field(..., description="YouTube playlist URL")

class PlaylistUpdate(BaseModel):
    \"\"\"Schema for updating a playlist\"\"\"
    title: Optional[str] = None
    excluded_ids: Optional[list[str]] = None

# Response schemas
class PlaylistResponse(BaseModel):
    \"\"\"Schema for playlist response\"\"\"
    id: int
    url: str
    title: str
    playlist_count: int
    local_count: int
    unavailable_count: int
    excluded_ids: list[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # For SQLAlchemy models
""", encoding='utf-8')
        print("  ✓ app/schemas/example.py")
    
    # Create example util file
    example_util = app / "utils" / "example.py"
    if not example_util.exists():
        example_util.write_text("""\"\"\"
Example utility functions
\"\"\"
import re
from pathlib import Path

def sanitize_filename(filename: str) -> str:
    \"\"\"
    Remove invalid characters from filename
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem
    \"\"\"
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    return filename

def is_valid_youtube_url(url: str) -> bool:
    \"\"\"
    Check if URL is a valid YouTube playlist URL
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid YouTube playlist URL
    \"\"\"
    pattern = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/(playlist|watch)\?.*list='
    return bool(re.match(pattern, url))

def ensure_directory(path: str | Path) -> Path:
    \"\"\"
    Ensure directory exists, create if not
    
    Args:
        path: Directory path
        
    Returns:
        Path object
    \"\"\"
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path
""", encoding='utf-8')
        print("  ✓ app/utils/example.py")
    
    # Create conftest.py for tests
    conftest = backend / "tests" / "conftest.py"
    if not conftest.exists():
        conftest.write_text("""\"\"\"
Pytest configuration and fixtures
\"\"\"
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.database import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    \"\"\"Database session fixture\"\"\"
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    \"\"\"Test client fixture\"\"\"
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
""", encoding='utf-8')
        print("  ✓ tests/conftest.py")
    
    # Create example test file
    example_test = backend / "tests" / "test_example.py"
    if not example_test.exists():
        example_test.write_text("""\"\"\"
Example test file
\"\"\"
import pytest

def test_example():
    \"\"\"Example test\"\"\"
    assert 1 + 1 == 2

def test_api_health(client):
    \"\"\"Test API health endpoint\"\"\"
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

# Add more tests here
""", encoding='utf-8')
        print("  ✓ tests/test_example.py")
    
    # Create .env.example if it doesn't exist
    env_example = backend / ".env.example"
    if not env_example.exists():
        env_example.write_text("""# Backend Environment Variables

# Database
DATABASE_URL=sqlite:///./yt_manager.db

# Download Settings
BASE_DOWNLOAD_PATH=downloads
MAX_CONCURRENT_DOWNLOADS=1
MAX_CONCURRENT_EXTRACTIONS=4

# Audio Settings
AUDIO_EXTRACT_MODE=copy

# Batch Settings
BATCH_SIZE=200

# Cookies (optional)
COOKIES_FILE=
USE_BROWSER_COOKIES=false
BROWSER_NAME=chrome

# API Settings
API_V1_STR=/api/v1
PROJECT_NAME=YouTube Playlist Manager

# CORS (comma-separated origins)
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
""", encoding='utf-8')
        print("  ✓ .env.example")
    
    print()
    print("="*60)
    print("Backend Reorganization Complete!")
    print("="*60)
    print()
    print("New Structure:")
    print("  backend/")
    print("    ├── app/")
    print("    │   ├── __init__.py")
    print("    │   ├── main.py              # Entry point")
    print("    │   ├── core/                # Config, core functionality")
    print("    │   │   ├── config.py")
    print("    │   │   └── yt_playlist_audio_tools.py")
    print("    │   ├── models/              # Database models")
    print("    │   │   └── database.py")
    print("    │   ├── schemas/             # Pydantic schemas (NEW)")
    print("    │   │   ├── example.py")
    print("    │   │   └── __init__.py")
    print("    │   ├── api/                 # API routes")
    print("    │   │   ├── v1/             # Version 1 (NEW)")
    print("    │   │   │   ├── endpoints/")
    print("    │   │   │   │   ├── playlists.py")
    print("    │   │   │   │   ├── downloads.py")
    print("    │   │   │   │   ├── config.py")
    print("    │   │   │   │   └── websocket.py")
    print("    │   │   │   ├── router.py")
    print("    │   │   │   └── __init__.py")
    print("    │   │   └── __init__.py")
    print("    │   ├── services/            # Business logic")
    print("    │   │   ├── job_manager.py")
    print("    │   │   └── ytdlp_service.py")
    print("    │   └── utils/               # Helper functions (NEW)")
    print("    │       ├── example.py")
    print("    │       └── __init__.py")
    print("    ├── tests/                   # Pytest tests (NEW)")
    print("    │   ├── conftest.py")
    print("    │   ├── test_example.py")
    print("    │   └── __init__.py")
    print("    ├── .env                     # Environment variables")
    print("    ├── .env.example             # Environment template")
    print("    ├── requirements.txt         # Dependencies")
    print("    └── run.py                   # Run script")
    print()
    print("Next Steps:")
    print("  1. Update main.py to use v1 router:")
    print("     from app.api.v1.router import router as v1_router")
    print("     app.include_router(v1_router, prefix='/api/v1')")
    print()
    print("  2. (Optional) Move old API files after verifying v1 works")
    print()
    print("  3. Create schemas for existing models")
    print("     - PlaylistCreate, PlaylistResponse")
    print("     - JobCreate, JobResponse")
    print("     - ConfigUpdate, ConfigResponse")
    print()
    print("  4. Add tests for API endpoints")
    print()

if __name__ == '__main__':
    reorganize_backend()
