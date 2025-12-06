# Schemas

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
