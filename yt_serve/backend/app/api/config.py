"""
Configuration API endpoints
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.core.config import settings

router = APIRouter()

class ConfigResponse(BaseModel):
    """Configuration response model"""
    base_download_path: str
    audio_extract_mode: str
    max_extraction_workers: int
    max_concurrent_downloads: int
    batch_size: int
    cookies_file: Optional[str]
    use_browser_cookies: bool
    browser_name: str

class ConfigUpdate(BaseModel):
    """Configuration update model"""
    base_download_path: Optional[str] = None
    audio_extract_mode: Optional[str] = None
    max_extraction_workers: Optional[int] = None
    max_concurrent_downloads: Optional[int] = None
    batch_size: Optional[int] = None
    cookies_file: Optional[str] = None
    use_browser_cookies: Optional[bool] = None
    browser_name: Optional[str] = None

@router.get("/", response_model=ConfigResponse)
async def get_config():
    """Get current configuration"""
    return ConfigResponse(
        base_download_path=settings.BASE_DOWNLOAD_PATH,
        audio_extract_mode=settings.AUDIO_EXTRACT_MODE,
        max_extraction_workers=settings.MAX_CONCURRENT_EXTRACTIONS,
        max_concurrent_downloads=settings.MAX_CONCURRENT_DOWNLOADS,
        batch_size=settings.BATCH_SIZE,
        cookies_file=settings.COOKIES_FILE,
        use_browser_cookies=settings.USE_BROWSER_COOKIES,
        browser_name=settings.BROWSER_NAME
    )

@router.put("/", response_model=ConfigResponse)
async def update_config(config: ConfigUpdate):
    """Update configuration"""
    # Update settings (in-memory for now)
    # In production, you'd want to persist these to a file or database
    
    if config.base_download_path is not None:
        settings.BASE_DOWNLOAD_PATH = config.base_download_path
    if config.audio_extract_mode is not None:
        settings.AUDIO_EXTRACT_MODE = config.audio_extract_mode
    if config.max_extraction_workers is not None:
        settings.MAX_CONCURRENT_EXTRACTIONS = config.max_extraction_workers
    if config.max_concurrent_downloads is not None:
        settings.MAX_CONCURRENT_DOWNLOADS = config.max_concurrent_downloads
    if config.batch_size is not None:
        settings.BATCH_SIZE = config.batch_size
    if config.cookies_file is not None:
        settings.COOKIES_FILE = config.cookies_file
    if config.use_browser_cookies is not None:
        settings.USE_BROWSER_COOKIES = config.use_browser_cookies
    if config.browser_name is not None:
        settings.BROWSER_NAME = config.browser_name
    
    return ConfigResponse(
        base_download_path=settings.BASE_DOWNLOAD_PATH,
        audio_extract_mode=settings.AUDIO_EXTRACT_MODE,
        max_extraction_workers=settings.MAX_CONCURRENT_EXTRACTIONS,
        max_concurrent_downloads=settings.MAX_CONCURRENT_DOWNLOADS,
        batch_size=settings.BATCH_SIZE,
        cookies_file=settings.COOKIES_FILE,
        use_browser_cookies=settings.USE_BROWSER_COOKIES,
        browser_name=settings.BROWSER_NAME
    )
