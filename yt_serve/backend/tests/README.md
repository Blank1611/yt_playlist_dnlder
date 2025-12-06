# Tests

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
