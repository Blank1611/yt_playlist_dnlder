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
COOKIES_FILE = CONFIG.get("cookies_file")
USER_AGENT = None
CONCURRENT_FRAGMENTS = 4


# ====== GLOBALS ======

SKIPPED_VIDEOS_ARCHIVE: List[Dict] = []
SKIPPED_AUDIO_EXISTING: List[Dict] = []
EXTRACTED_AUDIO: List[Dict] = []

GLOBAL_PROGRESS_CALLBACK = None  # set by GUI
GLOBAL_RUNSTATE = None           # SimpleNamespace(cancelled=bool) set by GUI

FAILED_VIDEO_IDS: Set[str] = set()  # IDs that failed in last download run


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


def _get_playlist_info_title(url: str) -> str:
    ydl_opts_info = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": "in_playlist",
    }
    with YoutubeDL(ydl_opts_info) as ydl:
        info = ydl.extract_info(url, download=False)
    return info.get("title") or "playlist"


def _build_playlist_paths(title: str) -> Tuple[str, str, str]:
    safe_title = _sanitize_title(title)
    playlist_folder = os.path.join(BASE_DOWNLOAD_PATH, safe_title)
    archive_file = os.path.join(playlist_folder, "archive.txt")
    audio_folder = os.path.join(playlist_folder, safe_title)

    os.makedirs(playlist_folder, exist_ok=True)
    os.makedirs(audio_folder, exist_ok=True)

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

def _progress_hook_archive(d):
    """
    Track:
      - items skipped because already downloaded / in archive
      - items that error out (FAILED_VIDEO_IDS)
    """
    global SKIPPED_VIDEOS_ARCHIVE, FAILED_VIDEO_IDS

    status = d.get("status")
    info = d.get("info_dict") or {}
    if info.get("_type") == "playlist":
        return

    vid = info.get("id")

    if status == "finished":
        downloaded = d.get("downloaded_bytes", 0) or d.get("total_bytes", 0)
        filename = d.get("filename") or info.get("filepath") or info.get("title")
        if not downloaded:
            SKIPPED_VIDEOS_ARCHIVE.append({
                "id": vid,
                "title": info.get("title") or filename or "Unknown",
                "reason": "already downloaded (archive/file)",
            })

    elif status == "error":
        err = d.get("error")
        msg = str(err)
        if vid:
            FAILED_VIDEO_IDS.add(vid)
        print(f"[WARN] Download failed for {vid}: {msg}")


def _slow_down_hook(d):
    if d.get("status") == "finished":
        if GLOBAL_RUNSTATE is not None and getattr(GLOBAL_RUNSTATE, "cancelled", False):
            print("Cancellation flag set. Skipping further delays.")
            return
        pause = random.uniform(3, 8)
        print(f"Pausing {pause:.1f}s to avoid hammering YouTube...")
        time.sleep(pause)


# ====== MODE 2: DOWNLOAD + EXTRACT ======

def download_playlist_with_video_and_audio(url: str, as_mp3: bool = True) -> Set[str]:
    """
    MODE 2:
      - Downloads bestvideo+bestaudio/best for a playlist/single video.
      - Uses download_archive to only get new videos.
      - If as_mp3 is True, extracts MP3 into audio subfolder.
    Returns:
      FAILED_VIDEO_IDS: set of failed/unavailable IDs for this run.
    """
    global SKIPPED_VIDEOS_ARCHIVE, FAILED_VIDEO_IDS
    SKIPPED_VIDEOS_ARCHIVE = []
    FAILED_VIDEO_IDS = set()

    print("Fetching playlist information...")
    try:
        title = _get_playlist_info_title(url)
    except Exception as e:
        print(f"Could not fetch playlist info ({e}), using generic name.")
        title = "playlist"

    playlist_folder, archive_file, audio_folder = _build_playlist_paths(title)

    print(f"\nBase path      : {BASE_DOWNLOAD_PATH}")
    print(f"Playlist title : {title}")
    print(f"Playlist folder: {playlist_folder}")
    print(f"Archive file   : {archive_file}")
    print(f"Audio folder   : {audio_folder}")

    common_opts = {
        "outtmpl": os.path.join(playlist_folder, "%(title)s.%(ext)s"),
        "ignoreerrors": True,
        "download_archive": archive_file,
        "quiet": False,
        "no_warnings": True,
        "progress_hooks": [_progress_hook_archive, _slow_down_hook],
    }
    if os.path.isfile(COOKIES_FILE):
        common_opts["cookies"] = COOKIES_FILE
    if USER_AGENT:
        common_opts["user_agent"] = USER_AGENT
    common_opts.update(_base_speed_opts())

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
    }
    ydl_opts.update(common_opts)

    print("\nStarting download...")
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    if SKIPPED_VIDEOS_ARCHIVE:
        print("\nVideos skipped (already in archive or on disk):")
        for v in SKIPPED_VIDEOS_ARCHIVE:
            print(f"  - {v.get('title') or 'Unknown'} [{v.get('id')}] — {v['reason']}")
    else:
        print("\nNo videos were skipped due to archive.")

    if as_mp3:
        print("\nExtracting audio to MP3 from downloaded videos...")
        extract_audio_for_existing_playlist_folder(playlist_folder, audio_folder)

    print(f"\nDone. Video files in:\n{playlist_folder}")
    print(f"MP3 files in:\n{audio_folder}")

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
