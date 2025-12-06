"""
Example test file
"""
import pytest

def test_example():
    """Example test"""
    assert 1 + 1 == 2

def test_api_health(client):
    """Test API health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

# Add more tests here
