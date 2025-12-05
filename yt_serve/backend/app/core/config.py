"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "YouTube Playlist Manager"
    
    # Database
    DATABASE_URL: str = "sqlite:///./yt_manager.db"
    
    # Download settings
    BASE_DOWNLOAD_PATH: str = "downloads"
    MAX_CONCURRENT_DOWNLOADS: int = 1
    MAX_CONCURRENT_EXTRACTIONS: int = 4
    
    # Audio settings
    AUDIO_EXTRACT_MODE: str = "copy"  # copy, mp3_best, mp3_high, opus
    
    # Batch settings
    BATCH_SIZE: int = 200
    
    # Cookies
    COOKIES_FILE: Optional[str] = None
    USE_BROWSER_COOKIES: bool = False
    BROWSER_NAME: str = "chrome"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
