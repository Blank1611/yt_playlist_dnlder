"""
Example utility functions
"""
import re
from pathlib import Path

def sanitize_filename(filename: str) -> str:
    """
    Remove invalid characters from filename
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\|?*]', '', filename)
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    return filename

def is_valid_youtube_url(url: str) -> bool:
    """
    Check if URL is a valid YouTube playlist URL
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid YouTube playlist URL
    """
    pattern = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/(playlist|watch)\?.*list='
    return bool(re.match(pattern, url))

def ensure_directory(path: str | Path) -> Path:
    """
    Ensure directory exists, create if not
    
    Args:
        path: Directory path
        
    Returns:
        Path object
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path
