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
    if USE_BROWSER_COOKIES:
        ydl_opts_info["cookies_from_browser"] = (BROWSER_NAME,)
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

def _get_playlist_entries(url: str, playlist_folder: str) -> List[dict]:
    """Return playlist entries (list of entry dicts), using cache when possible."""
    info = _get_playlist_info(url)
    playlist_entries = info.get("entries") or []
    with open(os.path.join(playlist_folder, "playlist_info.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
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

    # Get filtered video URLs (skip unavailable)
    entries = []
    try:
        entries = _get_playlist_entries(url, playlist_folder)
    except Exception as e:
        print(f"Warning: failed to enumerate playlist entries ({e}), will fall back to downloading the playlist URL.")

    video_urls: List[str] = []
    if entries:
        print(f"Found {len(entries)} entries; filtering unavailable/private items...")
        for e in entries:
            # Check cancellation during enumeration
            if GLOBAL_RUNSTATE is not None and getattr(GLOBAL_RUNSTATE, "cancelled", False):
                print("\n⚠️ Cancellation detected during entry filtering. Stopping...")
                return FAILED_VIDEO_IDS
            
            if not e:
                continue
            if is_entry_unavailable(e):
                vid = e.get("id") or e.get("url") or "unknown"
                print(f"  Skipping unavailable/private: {e.get('title') or vid} [{vid}]")
                if e.get("id"):
                    FAILED_VIDEO_IDS.add(e.get("id"))
                continue

            vid = e.get("id") or e.get("url")
            if not vid:
                continue
            if str(vid).startswith("http"):
                video_urls.append(str(vid))
            else:
                video_urls.append(f"https://www.youtube.com/watch?v={vid}")

    if not video_urls and entries:
        print("No available videos to download after filtering; nothing to do.")
        return FAILED_VIDEO_IDS

    common_opts = {
        "outtmpl": os.path.join(playlist_folder, "%(title)s.%(ext)s"),
        "ignoreerrors": True,
        "download_archive": archive_file,
        "quiet": False,
        "no_warnings": True,
        "progress_hooks": [_progress_hook_archive, _slow_down_hook],
    }

    if USE_BROWSER_COOKIES: #and _check_browser_cookies_available():
        print(f"✓ Loading cookies from {BROWSER_NAME} (browser is running)")
        common_opts["cookies_from_browser"] = (BROWSER_NAME,)
    elif COOKIES_FILE and os.path.isfile(COOKIES_FILE):
        print(f"✓ Loading cookies from file: {COOKIES_FILE}")
        common_opts["cookies"] = COOKIES_FILE
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

    print("\nStarting download...")
    
    # Download videos one by one so we can check cancellation between each
    try:
        with YoutubeDL(ydl_opts) as ydl:
            urls_to_download = video_urls if video_urls else [url]
            
            for idx, video_url in enumerate(urls_to_download):
                # Check cancellation BEFORE each video
                if GLOBAL_RUNSTATE is not None and getattr(GLOBAL_RUNSTATE, "cancelled", False):
                    print(f"\n⚠️ Cancellation detected at video {idx+1}/{len(urls_to_download)}. Stopping download...")
                    break
                
                try:
                    print(f"\n[{idx+1}/{len(urls_to_download)}] Downloading: {video_url}")
                    ydl.download([video_url])
                except KeyboardInterrupt:
                    print(f"\n⚠️ Download interrupted by user at video {idx+1}/{len(urls_to_download)}.")
                    break
                except Exception as e:
                    print(f"Error downloading {video_url}: {e}")
                    continue
    except Exception as e:
        print(f"\n❌ Download failed: {e}")

    if SKIPPED_VIDEOS_ARCHIVE:
        print("\nVideos skipped (already in archive or on disk):")
        for v in SKIPPED_VIDEOS_ARCHIVE:
            print(f"  - {v.get('title') or 'Unknown'} [{v.get('id')}] — {v['reason']}")

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
