"""
YouTube download service - wraps existing yt_playlist_audio_tools.py logic
"""
import sys
import os
from pathlib import Path
from typing import Set, Callable, Optional
import asyncio
from datetime import datetime

# Import download tools from backend core
try:
    from app.core import yt_playlist_audio_tools as tools
except ImportError as e:
    print(f"Warning: Could not import yt_playlist_audio_tools.py: {e}")
    tools = None

class DownloadService:
    """Service for downloading playlists using existing logic"""
    
    def __init__(self, base_path: str, config: dict):
        """Initialize download service"""
        self.base_path = base_path
        self.config = config
        self.current_runstate = None  # Track current job's runstate
        
        # Configure tools module if available
        if tools:
            tools.BASE_DOWNLOAD_PATH = base_path
            tools.AUDIO_EXTRACT_MODE = config.get("audio_extract_mode", "copy")
            tools.MAX_EXTRACTION_WORKERS = config.get("max_extraction_workers", 4)
            tools.BATCH_SIZE = config.get("batch_size", 200)
            tools.USE_BROWSER_COOKIES = config.get("use_browser_cookies", False)
            tools.BROWSER_NAME = config.get("browser_name", "chrome")
            tools.COOKIES_FILE = config.get("cookies_file")
    
    def cancel_current_job(self):
        """Cancel the currently running job"""
        if self.current_runstate:
            self.current_runstate.cancelled = True
    
    async def download_playlist(
        self,
        url: str,
        excluded_ids: Set[str],
        progress_callback: Optional[Callable] = None,
        log_callback: Optional[Callable] = None
    ) -> Set[str]:
        """
        Download playlist with progress and log callbacks
        
        Args:
            url: Playlist URL
            excluded_ids: Set of video IDs to exclude
            progress_callback: Async function(total, current, batch_info=None) for progress updates
            log_callback: Async function(message) for log messages
        
        Returns:
            Set of failed video IDs
        """
        if not tools:
            raise RuntimeError("yt_playlist_audio_tools not available")
        
        # Set up runstate for cancellation
        from types import SimpleNamespace
        runstate = SimpleNamespace(cancelled=False)
        self.current_runstate = runstate  # Store for cancellation
        tools.GLOBAL_RUNSTATE = runstate
        
        # Set up callbacks for existing tools
        if progress_callback:
            # Store the callback and loop for thread-safe calling
            main_loop = asyncio.get_event_loop()
            
            def sync_progress(total, current, batch_info=None):
                try:
                    # Use call_soon_threadsafe to schedule the callback in the main loop
                    asyncio.run_coroutine_threadsafe(
                        progress_callback(total, current, batch_info),
                        main_loop
                    )
                except Exception as e:
                    print(f"Progress callback error: {e}")
            
            tools.GLOBAL_PROGRESS_CALLBACK = sync_progress
        
        # Run download in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        failed_ids = await loop.run_in_executor(
            None,
            tools.download_playlist_with_video_and_audio,
            url,
            False,  # as_mp3 = False (extraction will be done separately in parallel)
            excluded_ids
        )
        
        return failed_ids
    
    async def extract_audio(
        self,
        playlist_title: str,
        progress_callback: Optional[Callable] = None,
        log_callback: Optional[Callable] = None
    ):
        """
        Extract audio from existing videos
        
        Args:
            playlist_title: Playlist title
            progress_callback: Async function(total, current) for progress updates
            log_callback: Async function(message) for log messages
        """
        if not tools:
            raise RuntimeError("yt_playlist_audio_tools not available")
        
        # Set up callbacks
        if progress_callback:
            # Store the callback and loop for thread-safe calling
            main_loop = asyncio.get_event_loop()
            
            def sync_progress(total, current):
                try:
                    # Use call_soon_threadsafe to schedule the callback in the main loop
                    asyncio.run_coroutine_threadsafe(
                        progress_callback(total, current),
                        main_loop
                    )
                except Exception as e:
                    print(f"Progress callback error: {e}")
            
            tools.GLOBAL_PROGRESS_CALLBACK = sync_progress
        
        # Run extraction in thread pool
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            tools.extract_audio_for_existing_playlist,
            playlist_title
        )
    
    async def get_playlist_info(self, url: str) -> dict:
        """Get playlist information"""
        if not tools:
            raise RuntimeError("yt_playlist_audio_tools not available")
        
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(
            None,
            tools._get_playlist_info,
            url,
            False  # force_refresh
        )
        
        return info
    
    async def get_playlist_stats(
        self,
        title: str,
        url: str,
        excluded_ids: list
    ) -> tuple:
        """Get playlist statistics"""
        if not tools:
            raise RuntimeError("yt_playlist_audio_tools not available")
        
        safe_title = tools._sanitize_title(title)
        playlist_folder = os.path.join(self.base_path, safe_title)
        
        # Count local videos
        local_count = 0
        if os.path.isdir(playlist_folder):
            video_exts = ("*.mp4", "*.mkv", "*.webm", "*.m4v")
            import glob
            files = []
            for pat in video_exts:
                files.extend(glob.glob(os.path.join(playlist_folder, pat)))
            local_count = len(files)
        
        # Get playlist entries
        loop = asyncio.get_event_loop()
        entries = await loop.run_in_executor(
            None,
            tools._get_playlist_entries,
            url,
            playlist_folder,
            False  # force_refresh
        )
        
        # Count available and unavailable
        excluded_set = set(excluded_ids or [])
        available_count = 0
        unavailable_count = 0
        
        for e in entries:
            if tools.is_entry_unavailable(e, excluded_set):
                unavailable_count += 1
            else:
                available_count += 1
        
        return local_count, available_count, unavailable_count
