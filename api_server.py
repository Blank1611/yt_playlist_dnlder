#!/usr/bin/env python3
"""
YouTube Playlist Manager - REST API Backend

FastAPI-based REST API for managing YouTube playlist downloads and audio extraction.
Designed to be consumed by a separate React frontend.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Set, Dict
from datetime import datetime
import json
import os
import threading
import queue
from contextlib import asynccontextmanager

import yt_playlist_audio_tools as tools

# ====== CONFIGURATION ======

CONFIG_FILE = "yt_playlist_gui_config.json"

default_config = {
    "base_path": tools.BASE_DOWNLOAD_PATH,
    "playlists": [],
}

# ====== GLOBAL STATE ======

# Task tracking
active_tasks: Dict[str, dict] = {}  # task_id -> task_info
task_logs: Dict[str, List[str]] = {}  # task_id -> log_lines
task_progress: Dict[str, dict] = {}  # task_id -> progress_info

# Thread-safe queue for logs
log_queues: Dict[str, queue.Queue] = {}


# ====== PYDANTIC MODELS ======

class PlaylistBase(BaseModel):
    url: str = Field(..., description="YouTube playlist URL")
    title: Optional[str] = Field(None, description="Playlist title (auto-fetched if not provided)")


class PlaylistCreate(PlaylistBase):
    pass


class Playlist(PlaylistBase):
    title: str
    last_download_ist: str = ""
    last_extract_ist: str = ""
    local_count: int = 0
    playlist_count: int = 0
    unavailable_count: int = 0
    excluded_ids: List[str] = []


class PlaylistUpdate(BaseModel):
    excluded_ids: Optional[List[str]] = None


class ConfigUpdate(BaseModel):
    base_path: Optional[str] = None


class TaskRequest(BaseModel):
    mode: str = Field(..., description="Operation mode: 'download_extract' or 'extract_only'")


class TaskStatus(BaseModel):
    task_id: str
    status: str  # 'running', 'completed', 'failed', 'cancelled'
    playlist_title: str
    mode: str
    progress: Optional[dict] = None
    started_at: str
    completed_at: Optional[str] = None


class LogResponse(BaseModel):
    logs: List[str]
    has_more: bool = False


# ====== CONFIG HELPERS ======

def load_config() -> dict:
    """Load configuration from JSON file."""
    if not os.path.isfile(CONFIG_FILE):
        return default_config.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in default_config.items():
            data.setdefault(k, v)
        for pl in data["playlists"]:
            pl.setdefault("last_download_ist", "")
            pl.setdefault("last_extract_ist", "")
            pl.setdefault("local_count", 0)
            pl.setdefault("playlist_count", 0)
            pl.setdefault("unavailable_count", 0)
            pl.setdefault("excluded_ids", [])
        return data
    except Exception:
        return default_config.copy()


def save_config(cfg: dict):
    """Save configuration to JSON file."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def get_playlist_stats(base_path: str, title: str, url: str, excluded_ids: list, force_refresh: bool = False):
    """Get playlist statistics."""
    safe_title = tools._sanitize_title(title)
    playlist_folder = os.path.join(base_path, safe_title)

    local_count = 0
    if os.path.isdir(playlist_folder):
        from glob import glob
        video_exts = ("*.mp4", "*.mkv", "*.webm", "*.m4v")
        files = []
        for pat in video_exts:
            files.extend(glob(os.path.join(playlist_folder, pat)))
        local_count = len(files)

    available_count = 0
    unavailable_count = 0
    excluded_set = set(excluded_ids or [])

    try:
        entries = tools._get_playlist_entries(url, playlist_folder, force_refresh=force_refresh)
        for e in entries:
            if tools.is_entry_unavailable(e, excluded_set):
                unavailable_count += 1
            else:
                available_count += 1
    except Exception:
        available_count = 0
        unavailable_count = 0

    return local_count, available_count, unavailable_count


# ====== TASK MANAGEMENT ======

class TaskLogger:
    """Logger that captures output to a queue for API consumption."""
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.queue = queue.Queue()
        log_queues[task_id] = self.queue
        task_logs[task_id] = []

    def write(self, s):
        if not s:
            return
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{ts}] {s}"
        self.queue.put(log_line)
        task_logs[self.task_id].append(log_line)

    def flush(self):
        pass


def run_playlist_task(task_id: str, playlist_idx: int, mode: str, url: str, title: str):
    """Background worker for playlist operations."""
    import sys
    from types import SimpleNamespace

    config = load_config()
    base_path = config["base_path"]
    
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    task_logger = TaskLogger(task_id)
    sys.stdout = task_logger
    sys.stderr = task_logger

    tools.BASE_DOWNLOAD_PATH = base_path
    runstate = SimpleNamespace(cancelled=False)

    def progress_cb(total, current_index):
        task_progress[task_id] = {
            "total": total,
            "current": current_index,
            "percentage": (current_index / total * 100) if total > 0 else 0
        }
        if runstate.cancelled:
            raise KeyboardInterrupt("Task cancelled")

    tools.GLOBAL_PROGRESS_CALLBACK = progress_cb
    tools.GLOBAL_RUNSTATE = runstate

    try:
        active_tasks[task_id]["status"] = "running"
        
        playlist_cfg = config["playlists"][playlist_idx]
        excluded_ids = set(playlist_cfg.get("excluded_ids", []))

        if mode == "download_extract":
            failed_ids = tools.download_playlist_with_video_and_audio(url, as_mp3=True, excluded_ids=excluded_ids)
            
            if not runstate.cancelled:
                # Update excluded IDs
                existing = set(playlist_cfg.get("excluded_ids", []))
                new_set = sorted(existing.union(failed_ids))
                playlist_cfg["excluded_ids"] = new_set
                
                # Update stats
                local_count, avail_count, unavail_count = get_playlist_stats(base_path, title, url, new_set)
                playlist_cfg["local_count"] = local_count
                playlist_cfg["playlist_count"] = avail_count
                playlist_cfg["unavailable_count"] = unavail_count
                playlist_cfg["last_download_ist"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                save_config(config)
                
        elif mode == "extract_only":
            tools.extract_audio_for_existing_playlist(title)
            
            if not runstate.cancelled:
                # Update stats
                local_count, avail_count, unavail_count = get_playlist_stats(
                    base_path, title, url, playlist_cfg["excluded_ids"]
                )
                playlist_cfg["local_count"] = local_count
                playlist_cfg["playlist_count"] = avail_count
                playlist_cfg["unavailable_count"] = unavail_count
                playlist_cfg["last_extract_ist"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                save_config(config)

        active_tasks[task_id]["status"] = "completed"
        active_tasks[task_id]["completed_at"] = datetime.now().isoformat()
        
    except KeyboardInterrupt:
        print("\n❌ Task cancelled by user")
        active_tasks[task_id]["status"] = "cancelled"
        active_tasks[task_id]["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        print(f"\n❌ Task failed: {e}")
        active_tasks[task_id]["status"] = "failed"
        active_tasks[task_id]["completed_at"] = datetime.now().isoformat()
        active_tasks[task_id]["error"] = str(e)
        
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        tools.GLOBAL_RUNSTATE = None


# ====== FASTAPI APP ======

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    print("YouTube Playlist Manager API starting...")
    yield
    # Shutdown
    print("YouTube Playlist Manager API shutting down...")


app = FastAPI(
    title="YouTube Playlist Manager API",
    description="REST API for managing YouTube playlist downloads and audio extraction",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ====== API ENDPOINTS ======

@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": "YouTube Playlist Manager API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/config")
async def get_config():
    """Get current configuration."""
    config = load_config()
    return {
        "base_path": config["base_path"],
        "playlist_count": len(config["playlists"])
    }


@app.put("/config")
async def update_config(config_update: ConfigUpdate):
    """Update configuration."""
    config = load_config()
    
    if config_update.base_path is not None:
        if not config_update.base_path.strip():
            raise HTTPException(status_code=400, detail="Base path cannot be empty")
        config["base_path"] = config_update.base_path
        tools.BASE_DOWNLOAD_PATH = config_update.base_path
    
    save_config(config)
    return {"message": "Configuration updated", "base_path": config["base_path"]}


@app.get("/playlists", response_model=List[Playlist])
async def list_playlists():
    """Get all playlists."""
    config = load_config()
    return config["playlists"]


@app.post("/playlists", response_model=Playlist)
async def create_playlist(playlist: PlaylistCreate):
    """Add a new playlist."""
    config = load_config()
    
    # Fetch title if not provided
    title = playlist.title
    if not title:
        try:
            title = tools._get_playlist_info_title(playlist.url)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not fetch playlist title: {e}")
    
    # Create playlist folder
    try:
        playlist_folder, archive_file, audio_folder = tools._build_playlist_paths(title, create_folders=True)
        
        # Save playlist_info.json
        try:
            entries = tools._get_playlist_entries(playlist.url, playlist_folder)
        except Exception:
            pass  # Non-critical
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not create playlist folder: {e}")
    
    # Get stats
    base_path = config["base_path"]
    local_count, avail_count, unavail_count = get_playlist_stats(base_path, title, playlist.url, [])
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_playlist = {
        "url": playlist.url,
        "title": title,
        "last_download_ist": now_str,
        "last_extract_ist": now_str,
        "local_count": local_count,
        "playlist_count": avail_count,
        "unavailable_count": unavail_count,
        "excluded_ids": [],
    }
    
    config["playlists"].append(new_playlist)
    save_config(config)
    
    return new_playlist


@app.get("/playlists/{playlist_idx}", response_model=Playlist)
async def get_playlist(playlist_idx: int):
    """Get a specific playlist."""
    config = load_config()
    
    if playlist_idx < 0 or playlist_idx >= len(config["playlists"]):
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    return config["playlists"][playlist_idx]


@app.put("/playlists/{playlist_idx}", response_model=Playlist)
async def update_playlist(playlist_idx: int, playlist_update: PlaylistUpdate):
    """Update a playlist."""
    config = load_config()
    
    if playlist_idx < 0 or playlist_idx >= len(config["playlists"]):
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    playlist = config["playlists"][playlist_idx]
    
    if playlist_update.excluded_ids is not None:
        playlist["excluded_ids"] = sorted(set(playlist_update.excluded_ids))
        
        # Refresh stats
        base_path = config["base_path"]
        local_count, avail_count, unavail_count = get_playlist_stats(
            base_path, playlist["title"], playlist["url"], playlist["excluded_ids"]
        )
        playlist["local_count"] = local_count
        playlist["playlist_count"] = avail_count
        playlist["unavailable_count"] = unavail_count
    
    save_config(config)
    return playlist


@app.delete("/playlists/{playlist_idx}")
async def delete_playlist(playlist_idx: int):
    """Remove a playlist."""
    config = load_config()
    
    if playlist_idx < 0 or playlist_idx >= len(config["playlists"]):
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    removed = config["playlists"].pop(playlist_idx)
    save_config(config)
    
    return {"message": "Playlist removed", "title": removed["title"]}


@app.post("/playlists/{playlist_idx}/refresh")
async def refresh_playlist(playlist_idx: int, force: bool = Query(False, description="Force refresh from API")):
    """Refresh playlist statistics."""
    config = load_config()
    
    if playlist_idx < 0 or playlist_idx >= len(config["playlists"]):
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    playlist = config["playlists"][playlist_idx]
    base_path = config["base_path"]
    
    local_count, avail_count, unavail_count = get_playlist_stats(
        base_path, playlist["title"], playlist["url"], playlist["excluded_ids"], force_refresh=force
    )
    
    playlist["local_count"] = local_count
    playlist["playlist_count"] = avail_count
    playlist["unavailable_count"] = unavail_count
    
    save_config(config)
    return playlist


@app.post("/playlists/{playlist_idx}/tasks", response_model=TaskStatus)
async def create_task(playlist_idx: int, task_request: TaskRequest, background_tasks: BackgroundTasks):
    """Start a download or extraction task."""
    config = load_config()
    
    if playlist_idx < 0 or playlist_idx >= len(config["playlists"]):
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    playlist = config["playlists"][playlist_idx]
    
    if task_request.mode not in ["download_extract", "extract_only"]:
        raise HTTPException(status_code=400, detail="Invalid mode. Must be 'download_extract' or 'extract_only'")
    
    # Check if task already running for this playlist
    for task_id, task_info in active_tasks.items():
        if (task_info["playlist_idx"] == playlist_idx and 
            task_info["status"] == "running"):
            raise HTTPException(
                status_code=409, 
                detail=f"Task already running for this playlist: {task_id}"
            )
    
    # Create task
    task_id = f"task_{playlist_idx}_{int(datetime.now().timestamp())}"
    
    task_info = {
        "task_id": task_id,
        "status": "pending",
        "playlist_idx": playlist_idx,
        "playlist_title": playlist["title"],
        "mode": task_request.mode,
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
    }
    
    active_tasks[task_id] = task_info
    task_progress[task_id] = {"total": 0, "current": 0, "percentage": 0}
    
    # Start background task
    background_tasks.add_task(
        run_playlist_task,
        task_id,
        playlist_idx,
        task_request.mode,
        playlist["url"],
        playlist["title"]
    )
    
    return TaskStatus(**task_info)


@app.get("/tasks", response_model=List[TaskStatus])
async def list_tasks():
    """Get all tasks."""
    tasks = []
    for task_id, task_info in active_tasks.items():
        progress = task_progress.get(task_id)
        tasks.append(TaskStatus(
            **task_info,
            progress=progress
        ))
    return tasks


@app.get("/tasks/{task_id}", response_model=TaskStatus)
async def get_task(task_id: str):
    """Get task status."""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_info = active_tasks[task_id]
    progress = task_progress.get(task_id)
    
    return TaskStatus(**task_info, progress=progress)


@app.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    """Cancel a running task."""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_info = active_tasks[task_id]
    
    if task_info["status"] != "running":
        raise HTTPException(status_code=400, detail="Task is not running")
    
    # Set cancellation flag
    if tools.GLOBAL_RUNSTATE:
        tools.GLOBAL_RUNSTATE.cancelled = True
    
    return {"message": "Cancellation requested", "task_id": task_id}


@app.get("/tasks/{task_id}/logs", response_model=LogResponse)
async def get_task_logs(
    task_id: str,
    offset: int = Query(0, description="Log line offset"),
    limit: int = Query(100, description="Maximum number of lines to return")
):
    """Get task logs."""
    if task_id not in task_logs:
        raise HTTPException(status_code=404, detail="Task not found or no logs available")
    
    logs = task_logs[task_id]
    total = len(logs)
    
    start = offset
    end = min(offset + limit, total)
    
    return LogResponse(
        logs=logs[start:end],
        has_more=end < total
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
