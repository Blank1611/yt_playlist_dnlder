#!/usr/bin/env python3
"""
yt_playlist_audio_tools.py

Shared tools for:
1) Downloading YouTube playlists with best video + audio and extracting MP3s.
2) Extracting MP3s later from already-downloaded playlist videos.

This version adds:
- GLOBAL_PROGRESS_CALLBACK: for GUI progress bar
- GLOBAL_RUNSTATE: for GUI cancel flag
- FAILED_VIDEO_IDS: IDs that failed (unavailable) in last run
- is_entry_unavailable(excluded_ids=...): uses per-playlist excluded_ids
"""

import os
import json
import time
import random
import shutil
import glob
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Set

from yt_dlp import YoutubeDL
from yt_dlp.utils import ExtractorError

def _load_config(config_path: str = "config.json") -> dict:
    """Load configuration from JSON file."""
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, "r") as f:
        return json.load(f)


CONFIG = _load_config()

# ====== USER CONFIG (DEFAULTS, CAN BE OVERRIDDEN BY GUI) ======

BASE_DOWNLOAD_PATH = CONFIG.get("base_download_path")
USE_BROWSER_COOKIES = CONFIG.get("use_browser_cookies", False)
BROWSER_NAME = CONFIG.get("browser_name", "chrome")  # chrome, firefox, edge, safari
COOKIES_FILE = CONFIG.get("cookies_file")
USER_AGENT = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36"
CONCURRENT_FRAGMENTS = 4


# ====== GLOBALS ======

SKIPPED_VIDEOS_ARCHIVE: List[Dict] = []
SKIPPED_AUDIO_EXISTING: List[Dict] = []
EXTRACTED_AUDIO: List[Dict] = []

GLOBAL_PROGRESS_CALLBACK = None  # set by GUI
GLOBAL_RUNSTATE = None           # SimpleNamespace(cancelled=bool) set by GUI

FAILED_VIDEO_IDS: Set[str] = set()  # IDs that failed in last download run
PLAYLIST_INFO_CACHE: Dict[str, dict] = {} # Cache for playlist info extracted via yt-dlp.extract_info()

# NEW global to let hooks know which playlist we're processing
GLOBAL_CURRENT_PLAYLIST_URL: Optional[str] = None


# ====== CUSTOM ARCHIVE LOGIC ======

def _load_custom_archive(archive_file: str) -> Set[str]:
    """Load video IDs from our custom archive file."""
    if not os.path.isfile(archive_file):
        return set()
    
    ids = set()
    with open(archive_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                # Extract ID from "youtube <id>" format or just "<id>"
                parts = line.split()
                vid_id = parts[-1] if parts else line
                ids.add(vid_id)
    return ids

def _save_custom_archive(archive_file: str, video_ids: Set[str]):
    """Save video IDs to our custom archive file."""
    os.makedirs(os.path.dirname(archive_file), exist_ok=True)
    with open(archive_file, "w", encoding="utf-8") as f:
        f.write("# Custom archive - video IDs successfully downloaded\n")
        for vid_id in sorted(video_ids):
            f.write(f"youtube {vid_id}\n")

def _add_to_custom_archive(archive_file: str, video_id: str):
    """Add a single video ID to the archive file."""
    with open(archive_file, "a", encoding="utf-8") as f:
        f.write(f"youtube {video_id}\n")

def _video_exists_on_disk(playlist_folder: str, video_id: str) -> bool:
    """Check if a video file with the given ID exists on disk."""
    video_exts = ("*.mp4", "*.mkv", "*.webm", "*.m4v")
    for pattern in video_exts:
        files = glob.glob(os.path.join(playlist_folder, pattern))
        for file in files:
            # Check if video ID is in filename (format: [video_id])
            if f"[{video_id}]" in file or f"_{video_id}." in file:
                return True
    return False

def _should_download_video(archive_file: str, playlist_folder: str, video_id: str) -> bool:
    """
    Determine if a video should be downloaded based on:
    a. ID does not exist in archive.txt, OR
    b. ID exists in archive but file not actually on disk
    """
    archived_ids = _load_custom_archive(archive_file)
    
    # Case a: Not in archive at all
    if video_id not in archived_ids:
        return True
    
    # Case b: In archive but file missing on disk
    if not _video_exists_on_disk(playlist_folder, video_id):
        print(f"  ⚠️  Video {video_id} in archive but missing on disk - will re-download")
        return True
    
    return False

# ====== HELPERS ======

def _find_ffmpeg_windows() -> Optional[str]:
    possible_names = ['ffmpeg.exe', 'ffmpeg']
    for name in possible_names:
        path = shutil.which(name)
        if path:
            return path

    common_paths = [
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        r"%LOCALAPPDATA%\Programs\ffmpeg\bin\ffmpeg.exe",
    ]
    for path_template in common_paths:
        path = os.path.expandvars(path_template)
        if os.path.exists(path):
            return path

    return None


def _sanitize_title(title: str) -> str:
    safe_title = "".join(c for c in title if c not in r'\/:*?"<>|').strip()
    return safe_title or "playlist"

def _get_playlist_info(url: str, force_refresh: bool = False) -> dict:
    """Return the full info dict for a playlist/url, caching the result.

    If force_refresh is True, re-run extract_info and update cache.
    """
    if not force_refresh and url in PLAYLIST_INFO_CACHE:
        return PLAYLIST_INFO_CACHE[url]

    ydl_opts_info = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": "in_playlist",
    }
    if USE_BROWSER_COOKIES and _check_browser_cookies_available():
        ydl_opts_info["cookies_from_browser"] = (BROWSER_NAME,)
    elif COOKIES_FILE and os.path.isfile(COOKIES_FILE):
        # yt-dlp Python API expects "cookiefile" for a cookies.txt path
        ydl_opts_info["cookiefile"] = COOKIES_FILE
    if USER_AGENT:
        ydl_opts_info["user_agent"] = USER_AGENT

    try:
        with YoutubeDL(ydl_opts_info) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        # don't overwrite existing cached info on transient failures
        if url in PLAYLIST_INFO_CACHE and not force_refresh:
            return PLAYLIST_INFO_CACHE[url]
        raise

    PLAYLIST_INFO_CACHE[url] = info or {}
    return PLAYLIST_INFO_CACHE[url]

def _get_playlist_info_title(url: str) -> str:
    info = _get_playlist_info(url)
    return info.get("title") or "playlist"

def _save_playlist_info_with_versioning(playlist_folder: str, info: dict):
    """
    Save playlist_info.json to the playlist_info_snapshot subdirectory.
    If file already exists, rename old file with creation date before saving new one.
    """
    # Create snapshot subdirectory
    snapshot_dir = os.path.join(playlist_folder, "playlist_info_snapshot")
    os.makedirs(snapshot_dir, exist_ok=True)
    
    info_path = os.path.join(snapshot_dir, "playlist_info.json")
    
    # If file exists, rename it with its creation date
    if os.path.isfile(info_path):
        try:
            # Get file creation time
            creation_time = os.path.getctime(info_path)
            date_str = datetime.fromtimestamp(creation_time).strftime("%Y%m%d_%H%M%S")
            
            # Rename old file in same directory
            old_name = os.path.join(snapshot_dir, f"playlist_info_{date_str}.json")
            os.rename(info_path, old_name)
            print(f"  Archived old playlist_info.json as: {os.path.basename(old_name)}")
        except Exception as e:
            print(f"  Warning: Could not archive old playlist_info.json: {e}")
    
    # Save new file
    with open(info_path, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    
    print(f"  Saved playlist_info.json to: playlist_info_snapshot/")

def _get_playlist_entries(url: str, playlist_folder: str) -> List[dict]:
    """Return playlist entries (list of entry dicts), using cache when possible."""
    info = _get_playlist_info(url)
    playlist_entries = info.get("entries") or []
    _save_playlist_info_with_versioning(playlist_folder, info)
    return playlist_entries

def _check_browser_cookies_available(browser_name: str = BROWSER_NAME) -> bool:
    """
    Return True if browser cookies for YouTube can be loaded (requires browser_cookie3).
    If browser_cookie3 is not installed or no youtube cookies found, returns False.
    """
    try:
        import browser_cookie3
    except Exception as e:
        # browser_cookie3 not installed or import failed
        print(f"[WARN] browser_cookie3 not available: {e}")
        return False

    try:
        loader = getattr(browser_cookie3, browser_name.lower(), None)
        if not callable(loader):
            # unsupported browser
            return False
        cj = loader()
        # cj is a CookieJar; check for any cookie that mentions youtube
        for cookie in cj:
            domain = getattr(cookie, "domain", "") or ""
            if "youtube" in domain.lower() or "google" in domain.lower():
                return True
        return False
    except Exception as e:
        print(f"[WARN] Failed to inspect browser cookies: {e}")
        return False

def _build_playlist_paths(title: str, create_folders: bool = True) -> Tuple[str, str, str]:
    """
    Build paths for playlist folder, archive file, and audio folder.
    If create_folders is True, creates the folders immediately including playlist_info_snapshot.
    """
    safe_title = _sanitize_title(title)
    playlist_folder = os.path.join(BASE_DOWNLOAD_PATH, safe_title)
    archive_file = os.path.join(playlist_folder, "archive.txt")
    audio_folder = os.path.join(playlist_folder, safe_title)
    snapshot_folder = os.path.join(playlist_folder, "playlist_info_snapshot")

    if create_folders:
        os.makedirs(playlist_folder, exist_ok=True)
        os.makedirs(audio_folder, exist_ok=True)
        os.makedirs(snapshot_folder, exist_ok=True)

    return playlist_folder, archive_file, audio_folder


def _base_speed_opts() -> dict:
    return {
        "concurrent_fragment_downloads": CONCURRENT_FRAGMENTS,
        "continuedl": True,
        "retries": 5,
        "fragment_retries": 5,
        "noprogress": False,
    }


# ====== UNAVAILABLE ENTRY DETECTION ======

def is_entry_unavailable(e: dict, excluded_ids: Set[str] | None = None) -> bool:
    """Heuristic to detect unavailable videos for playlist statistics."""
    if e is None:
        return True

    vid = e.get("id")
    if excluded_ids and vid in excluded_ids:
        return True
    if vid in FAILED_VIDEO_IDS:
        return True

    title_e = (e.get("title") or "").lower()
    desc_e = (e.get("description") or "").lower()
    err_e = (e.get("error") or e.get("error_text") or "").lower()
    text = " ".join([title_e, desc_e, err_e])

    patterns = [
        "private video",
        "deleted video",
        "video unavailable",
        "this video is not available",
        "has been removed by the uploader",
        "no longer available due to a copyright claim",
        "this content isn",  # "isn't available" variants
    ]
    for ph in patterns:
        if ph in text:
            return True

    availability = (e.get("availability") or "").lower()
    if availability and availability != "public":
        return True

    return False


# ====== YT-DLP HOOKS ======

def _load_gui_config() -> dict:
    cfg_path = os.path.join(os.path.dirname(__file__), "yt_playlist_gui_config.json")
    if not os.path.isfile(cfg_path):
        return {}
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Could not read GUI config: {e}")
        return {}

def _save_gui_config(cfg: dict) -> None:
    cfg_path = os.path.join(os.path.dirname(__file__), "yt_playlist_gui_config.json")
    try:
        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[WARN] Could not save GUI config: {e}")

def _add_excluded_id_to_gui_config(playlist_url: str, vid: str) -> None:
    """Append vid to the playlist's excluded_ids in the GUI config (if not present)."""
    if not playlist_url or not vid:
        return
    cfg = _load_gui_config()
    playlists = cfg.get("playlists") or []
    updated = False
    for p in playlists:
        if p.get("url") == playlist_url:
            excluded = p.get("excluded_ids") or []
            if vid not in excluded:
                excluded.append(vid)
                p["excluded_ids"] = excluded
                p["unavailable_count"] = int(p.get("unavailable_count", 0)) + 1
                updated = True
            break
    if updated:
        _save_gui_config(cfg)

def _progress_hook_custom(d):
    """
    Track download progress and errors.
    Note: With custom archive logic, we don't rely on this for skipped videos,
    but we still use it to catch errors reported by yt-dlp's hook system.
    """
    global FAILED_VIDEO_IDS, GLOBAL_CURRENT_PLAYLIST_URL

    status = d.get("status")
    info = d.get("info_dict") or {}
    if info.get("_type") == "playlist":
        return

    vid = info.get("id")

    if status == "error":
        err = d.get("error")
        msg = str(err)
        if vid:
            FAILED_VIDEO_IDS.add(vid)
            print(f"[WARN] Download failed (hook) for {vid}: {msg}")
            # persist immediately into GUI config excluded_ids so next runs skip it
            try:
                if GLOBAL_CURRENT_PLAYLIST_URL:
                    _add_excluded_id_to_gui_config(GLOBAL_CURRENT_PLAYLIST_URL, vid)
            except Exception as e:
                print(f"[WARN] Could not persist failed id {vid}: {e}")


def _slow_down_hook(d):
    if d.get("status") == "finished":
        if GLOBAL_RUNSTATE is not None and getattr(GLOBAL_RUNSTATE, "cancelled", False):
            print("Cancellation flag set. Skipping further delays.")
            return
        pause = random.uniform(3, 8)
        print(f"Pausing {pause:.1f}s to avoid hammering YouTube...")
        time.sleep(pause)


# ====== MODE 2: DOWNLOAD + EXTRACT ======

# def download_playlist_with_video_and_audio(url: str, as_mp3: bool = True) -> Set[str]:
#     """
#     MODE 2:
#       - Downloads bestvideo+bestaudio/best for a playlist/single video.
#       - Uses download_archive to only get new videos.
#       - If as_mp3 is True, extracts MP3 into audio subfolder.
#     Returns:
#       FAILED_VIDEO_IDS: set of failed/unavailable IDs for this run.
#     """
#     global SKIPPED_VIDEOS_ARCHIVE, FAILED_VIDEO_IDS
#     SKIPPED_VIDEOS_ARCHIVE = []
#     FAILED_VIDEO_IDS = set()

#     print("Fetching playlist information...")
#     try:
#         title = _get_playlist_info_title(url)
#     except Exception as e:
#         print(f"Could not fetch playlist info ({e}), using generic name.")
#         title = "playlist"

#     playlist_folder, archive_file, audio_folder = _build_playlist_paths(title)

#     print(f"\nBase path      : {BASE_DOWNLOAD_PATH}")
#     print(f"Playlist title : {title}")
#     print(f"Playlist folder: {playlist_folder}")
#     print(f"Archive file   : {archive_file}")
#     print(f"Audio folder   : {audio_folder}")

#     common_opts = {
#         "outtmpl": os.path.join(playlist_folder, "%(title)s.%(ext)s"),
#         "ignoreerrors": True,
#         "download_archive": archive_file,
#         "quiet": False,
#         "no_warnings": True,
#         "progress_hooks": [_progress_hook_archive, _slow_down_hook],
#     }

#     if USE_BROWSER_COOKIES:
#         common_opts["cookies_from_browser"] = (BROWSER_NAME,)
#     else:
#         if COOKIES_FILE and os.path.isfile(COOKIES_FILE):
#             common_opts["cookies"] = COOKIES_FILE

#     if USER_AGENT:
#         common_opts["user_agent"] = USER_AGENT
#     common_opts.update(_base_speed_opts())

#     ydl_opts = {
#         "format": "bestvideo+bestaudio/best",
#         "merge_output_format": "mp4",
#     }
#     ydl_opts.update(common_opts)

#     # First try to enumerate playlist entries (uses cached _get_playlist_entries)
#     entries = []
#     try:
#         entries = _get_playlist_entries(url, playlist_folder)
#     except Exception as e:
#         # _get_playlist_entries may raise on transient failures; fall back to direct download below
#         print(f"Warning: failed to enumerate playlist entries ({e}), will fall back to downloading the playlist URL.")

#     video_urls: List[str] = []
#     if entries:
#         print(f"Found {len(entries)} entries; filtering unavailable/private items...")
#         for e in entries:
#             if not e:
#                 continue
#             # skip entries detected as unavailable/private by heuristic
#             if is_entry_unavailable(e):
#                 vid = e.get("id") or e.get("url") or "unknown"
#                 print(f"  Skipping unavailable/private: {e.get('title') or vid} [{vid}]")
#                 # mark in FAILED_VIDEO_IDS so stats reflect it
#                 if e.get("id"):
#                     FAILED_VIDEO_IDS.add(e.get("id"))
#                 continue

#             # build full watch URL where necessary
#             vid = e.get("id") or e.get("url")
#             if not vid:
#                 continue
#             if str(vid).startswith("http"):
#                 video_urls.append(str(vid))
#             else:
#                 video_urls.append(f"https://www.youtube.com/watch?v={vid}")

#         if not video_urls:
#             print("No available videos to download after filtering; nothing to do.")
#     else:
#         # entries empty => fall back to playlist URL (single video or yt-dlp will expand)
#         print("Could not get entries list; falling back to downloading the provided URL.")

#     # Start download: prefer list of filtered URLs when available
#     print("\nStarting download...")
#     try:
#         with YoutubeDL(ydl_opts) as ydl:
#             if video_urls:
#                 ydl.download(video_urls)
#             else:
#                 ydl.download([url])
#     except Exception as e:
#         # ensure we capture any failed IDs already added by progress hook; re-raise if needed
#         print(f"[ERROR] Download run raised an exception: {e}")

#     if SKIPPED_VIDEOS_ARCHIVE:
#         print("\nVideos skipped (already in archive or on disk):")
#         for v in SKIPPED_VIDEOS_ARCHIVE:
#             print(f"  - {v.get('title') or 'Unknown'} [{v.get('id')}] — {v['reason']}")
#     else:
#         print("\nNo videos were skipped due to archive.")

#     if as_mp3:
#         print("\nExtracting audio to MP3 from downloaded videos...")
#         extract_audio_for_existing_playlist_folder(playlist_folder, audio_folder)

#     print(f"\nDone. Video files in:\n{playlist_folder}")
#     print(f"MP3 files in:\n{audio_folder}")

#     return FAILED_VIDEO_IDS

def download_playlist_with_video_and_audio(url: str, as_mp3: bool = True, excluded_ids: Set[str] | None = None) -> Set[str]:
    """
    MODE 2:
      - Downloads bestvideo+bestaudio/best for a playlist/single video.
      - Uses CUSTOM archive logic (not yt-dlp's download_archive).
      - Downloads only if: (a) ID not in archive.txt OR (b) ID in archive but file missing on disk
      - After successful download, verifies file exists then updates archive.txt
      - If as_mp3 is True, extracts MP3 into audio subfolder.
      - excluded_ids: set of video IDs to skip (from GUI config)
    Returns:
      FAILED_VIDEO_IDS: set of failed/unavailable IDs for this run.
    """
    global SKIPPED_VIDEOS_ARCHIVE, FAILED_VIDEO_IDS, GLOBAL_CURRENT_PLAYLIST_URL
    SKIPPED_VIDEOS_ARCHIVE = []
    FAILED_VIDEO_IDS = set()
    GLOBAL_CURRENT_PLAYLIST_URL = url  # set for hooks

    if excluded_ids is None:
        excluded_ids = set()

    try:
        print("Fetching playlist information...")
        title = _get_playlist_info_title(url)

        # Create folders immediately when playlist is added
        playlist_folder, archive_file, audio_folder = _build_playlist_paths(title, create_folders=True)

        print(f"\nBase path      : {BASE_DOWNLOAD_PATH}")
        print(f"Playlist title : {title}")
        print(f"Playlist folder: {playlist_folder}")
        print(f"Archive file   : {archive_file}")
        print(f"Audio folder   : {audio_folder}")

        # Load custom archive
        archived_ids = _load_custom_archive(archive_file)
        print(f"Loaded {len(archived_ids)} IDs from custom archive")

        # Get filtered video URLs (skip unavailable)
        entries = []
        try:
            entries = _get_playlist_entries(url, playlist_folder)
        except Exception as e:
            print(f"Warning: failed to enumerate playlist entries ({e}), will fall back to downloading the playlist URL.")

        videos_to_download: List[Tuple[str, str]] = []  # (video_id, video_url)
        
        if entries:
            print(f"Found {len(entries)} entries; filtering based on custom archive logic...")
            for e in entries:
                # Check cancellation during enumeration
                if GLOBAL_RUNSTATE is not None and getattr(GLOBAL_RUNSTATE, "cancelled", False):
                    print("\n⚠️ Cancellation detected during entry filtering. Stopping...")
                    return FAILED_VIDEO_IDS
                
                if not e:
                    continue
                
                vid = e.get("id") or e.get("url") or "unknown"
                
                # Skip if in excluded_ids (from GUI config)
                if vid in excluded_ids:
                    print(f"  Skipping (excluded): {e.get('title') or vid} [{vid}]")
                    FAILED_VIDEO_IDS.add(vid)
                    continue
                
                # Skip if detected as unavailable/private by heuristic
                if is_entry_unavailable(e, excluded_ids=excluded_ids):
                    print(f"  Skipping unavailable/private: {e.get('title') or vid} [{vid}]")
                    if e.get("id"):
                        FAILED_VIDEO_IDS.add(e.get("id"))
                    continue

                if not vid:
                    continue
                
                # CUSTOM ARCHIVE LOGIC: Check if we should download
                if not _should_download_video(archive_file, playlist_folder, vid):
                    print(f"  ✓ Already downloaded: {e.get('title') or vid} [{vid}]")
                    SKIPPED_VIDEOS_ARCHIVE.append({
                        "id": vid,
                        "title": e.get('title') or vid,
                        "reason": "already in custom archive and file exists on disk",
                    })
                    continue
                
                # Add to download list
                if str(vid).startswith("http"):
                    video_url = str(vid)
                else:
                    video_url = f"https://www.youtube.com/watch?v={vid}"
                
                videos_to_download.append((vid, video_url))

        if not videos_to_download and entries:
            print("No new videos to download after filtering; all up to date.")
            return FAILED_VIDEO_IDS

        # Prepare yt-dlp options WITHOUT download_archive (we manage it ourselves)
        common_opts = {
            "outtmpl": os.path.join(playlist_folder, "%(title)s [%(id)s].%(ext)s"),  # Include ID in filename
            "ignoreerrors": False,
            # NO download_archive - we manage it ourselves
            "quiet": False,
            "no_warnings": True,
            "progress_hooks": [_progress_hook_custom, _slow_down_hook],  # Keep hook to catch yt-dlp errors
        }

        if USE_BROWSER_COOKIES:
            print(f"✓ Loading cookies from {BROWSER_NAME} (browser is running)")
            common_opts["cookies_from_browser"] = (BROWSER_NAME,)
        elif COOKIES_FILE and os.path.isfile(COOKIES_FILE):
            print(f"✓ Loading cookies from file: {COOKIES_FILE}")
            common_opts["cookiefile"] = COOKIES_FILE
        else:
            print("⚠️  Warning: No valid cookies found. Age-restricted videos will likely fail.")

        if USER_AGENT:
            common_opts["user_agent"] = USER_AGENT
        common_opts.update(_base_speed_opts())

        ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
        }
        ydl_opts.update(common_opts)

        print(f"\nStarting download of {len(videos_to_download)} new videos...")
        
        # Download videos one by one with custom archive management
        successfully_downloaded = []
        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                for idx, (vid, video_url) in enumerate(videos_to_download, 1):
                    # Check cancellation BEFORE each video
                    if GLOBAL_RUNSTATE is not None and getattr(GLOBAL_RUNSTATE, "cancelled", False):
                        print(f"\n⚠️ Cancellation detected at video {idx}/{len(videos_to_download)}. Stopping download...")
                        break
                    
                    try:
                        print(f"\n[{idx}/{len(videos_to_download)}] Downloading: {vid}")
                        ydl.download([video_url])
                        
                        # VERIFY file exists on disk before adding to archive
                        if _video_exists_on_disk(playlist_folder, vid):
                            print(f"  ✓ Download verified, adding {vid} to archive")
                            _add_to_custom_archive(archive_file, vid)
                            successfully_downloaded.append(vid)
                        else:
                            print(f"  ⚠️  Download completed but file not found on disk for {vid}")
                            FAILED_VIDEO_IDS.add(vid)
                            
                    except Exception as e:
                        print(f"[WARN] Download failed for {vid}: {str(e)}")
                        FAILED_VIDEO_IDS.add(vid)
                        
                        # Persist to GUI config immediately
                        try:
                            if GLOBAL_CURRENT_PLAYLIST_URL:
                                _add_excluded_id_to_gui_config(GLOBAL_CURRENT_PLAYLIST_URL, vid)
                        except Exception as persist_err:
                            print(f"[WARN] Could not persist failed id {vid}: {persist_err}")
                        continue
                        
        except Exception as e:
            print(f"\n❌ Download run failed: {e}")

        print(f"\n✓ Successfully downloaded and archived: {len(successfully_downloaded)} videos")
        
        if SKIPPED_VIDEOS_ARCHIVE:
            print(f"\nVideos skipped (already downloaded): {len(SKIPPED_VIDEOS_ARCHIVE)}")

        if as_mp3:
            # Check if cancelled before extracting
            if GLOBAL_RUNSTATE is not None and getattr(GLOBAL_RUNSTATE, "cancelled", False):
                print("\n⚠️ Cancellation requested. Skipping audio extraction.")
            else:
                print("\nExtracting audio to MP3 from downloaded videos...")
                try:
                    extract_audio_for_existing_playlist_folder(playlist_folder, audio_folder)
                except KeyboardInterrupt:
                    print("\n⚠️ Audio extraction cancelled by user.")

        # Merge failed ids into GUI config as final step
        if FAILED_VIDEO_IDS:
            try:
                for vid in list(FAILED_VIDEO_IDS):
                    _add_excluded_id_to_gui_config(url, vid)
            except Exception as e:
                print(f"[WARN] Could not merge failed IDs into GUI config: {e}")

    finally:
        GLOBAL_CURRENT_PLAYLIST_URL = None

    return FAILED_VIDEO_IDS

# ====== MODE 1: EXTRACT FROM EXISTING ======

def extract_audio_for_existing_playlist(title: str):
    safe_title = _sanitize_title(title)
    playlist_folder = os.path.join(BASE_DOWNLOAD_PATH, safe_title)
    audio_folder = os.path.join(playlist_folder, safe_title)
    os.makedirs(audio_folder, exist_ok=True)
    extract_audio_for_existing_playlist_folder(playlist_folder, audio_folder)


def extract_audio_for_existing_playlist_folder(playlist_folder: str, audio_folder: str):
    global SKIPPED_AUDIO_EXISTING, EXTRACTED_AUDIO
    SKIPPED_AUDIO_EXISTING = []
    EXTRACTED_AUDIO = []

    if not os.path.isdir(playlist_folder):
        print(f"Playlist folder does not exist: {playlist_folder}")
        return

    ffmpeg_path = _find_ffmpeg_windows()
    if not ffmpeg_path:
        print("FFmpeg not found; cannot extract audio.")
        return

    print(f"\nUsing FFmpeg at: {ffmpeg_path}")
    print(f"Scanning for video files in: {playlist_folder}")
    print(f"Writing MP3s to: {audio_folder}\n")

    video_exts = ("*.mp4", "*.mkv", "*.webm", "*.m4v")
    video_files: List[str] = []
    for pattern in video_exts:
        video_files.extend(glob.glob(os.path.join(playlist_folder, pattern)))

    if not video_files:
        print("No video files found to extract audio from.")
        return

    from subprocess import run, DEVNULL, CalledProcessError

    total = len(video_files)
    for idx, vid_path in enumerate(video_files, start=1):
        if GLOBAL_RUNSTATE is not None and getattr(GLOBAL_RUNSTATE, "cancelled", False):
            print("Cancellation requested. Stopping extraction loop.")
            break

        base_name = os.path.splitext(os.path.basename(vid_path))[0]
        mp3_path = os.path.join(audio_folder, base_name + ".mp3")

        if GLOBAL_PROGRESS_CALLBACK is not None:
            GLOBAL_PROGRESS_CALLBACK(total, idx)

        if os.path.isfile(mp3_path):
            SKIPPED_AUDIO_EXISTING.append({"video": vid_path, "audio": mp3_path})
            continue

        cmd = [
            ffmpeg_path,
            "-y",
            "-i", vid_path,
            "-vn",
            "-acodec", "libmp3lame",
            "-qscale:a", "2",
            mp3_path,
        ]
        print(f"Extracting: {os.path.basename(vid_path)} -> {os.path.basename(mp3_path)}")
        try:
            run(cmd, stdout=DEVNULL, stderr=DEVNULL, check=True)
            EXTRACTED_AUDIO.append({"video": vid_path, "audio": mp3_path})
        except CalledProcessError:
            print(f"  ! ffmpeg failed for {vid_path}")

        time.sleep(random.uniform(0.5, 1.5))

    print("\nAudio extraction summary:")
    print(f"  Extracted MP3s: {len(EXTRACTED_AUDIO)}")
    print(f"  Skipped (already had MP3): {len(SKIPPED_AUDIO_EXISTING)}")

    if SKIPPED_AUDIO_EXISTING:
        print("\nSkipped because MP3 already exists:")
        for item in SKIPPED_AUDIO_EXISTING:
            print(f"  - {os.path.basename(item['audio'])}")

    if EXTRACTED_AUDIO:
        print("\nNewly created MP3s:")
        for item in EXTRACTED_AUDIO:
            print(f"  - {os.path.basename(item['audio'])}")
