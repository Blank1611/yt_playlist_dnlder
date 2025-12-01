#!/usr/bin/env python3
"""
yt_playlist_manager_gui.py

GUI wrapper for yt_playlist_audio_tools with:
- Table:
    Playlist | Last download | Last extract | Local videos | Playlist videos | Unavailable | URL
- Row highlight when local videos != downloadable playlist videos
- On startup, recomputes stats for all saved playlists and logs to app_startup.log
- For each playlist operation, logs to logs/<sanitized_playlist_title>.log
- Per-playlist excluded_ids: stored in config, auto-filled from failed downloads,
  and manually editable via GUI.
"""

import json
import os
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime
from glob import glob
from types import SimpleNamespace
from concurrent.futures import ThreadPoolExecutor, as_completed

from yt_dlp import YoutubeDL
import yt_playlist_audio_tools as tools  # helper module


# ---------- LOGGING HELPERS ----------

# STARTUP_LOG will be set dynamically based on base_path from config
# Initially None until config is loaded
STARTUP_LOG = None


def get_startup_log_path(base_path: str) -> str:
    """Get the startup log path in the base download path."""
    logs_dir = get_logs_base_dir(base_path)
    return os.path.join(logs_dir, "app_startup.log")


def get_logs_base_dir(base_path: str) -> str:
    """Get the logs directory in the base download path."""
    logs_dir = os.path.join(base_path, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir


def get_playlist_log_path(base_path: str, playlist_title: str) -> str:
    """Get the log file path for a specific playlist."""
    logs_dir = get_logs_base_dir(base_path)
    safe_title = sanitize_for_filename(playlist_title)
    playlist_log_dir = os.path.join(logs_dir, safe_title)
    os.makedirs(playlist_log_dir, exist_ok=True)
    return os.path.join(playlist_log_dir, f"{safe_title}.log")

# Log rotation settings (can be overridden by config)
MAX_LOG_LINES = 5000  # Rotate after 5000 lines
MAX_LOG_SIZE_MB = 10  # Rotate after 10 MB


def _load_log_rotation_settings():
    """Load log rotation settings from config if available."""
    global MAX_LOG_LINES, MAX_LOG_SIZE_MB
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                MAX_LOG_LINES = config.get("max_log_lines", MAX_LOG_LINES)
                MAX_LOG_SIZE_MB = config.get("max_log_size_mb", MAX_LOG_SIZE_MB)
    except Exception:
        pass  # Use defaults if config can't be loaded


_load_log_rotation_settings()


def sanitize_for_filename(name: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in name).strip("_") or "playlist"


def _rotate_log_if_needed(log_path: str) -> None:
    """
    Rotate log file if it exceeds size or line limits.
    Renamed format: basename_YYYYMMDD_revision.log
    """
    if not os.path.exists(log_path):
        return
    
    # Check file size
    file_size_mb = os.path.getsize(log_path) / (1024 * 1024)
    
    # Check line count
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            line_count = sum(1 for _ in f)
    except Exception:
        line_count = 0
    
    # Rotate if exceeds limits
    if file_size_mb > MAX_LOG_SIZE_MB or line_count > MAX_LOG_LINES:
        # Get file creation/modification time
        file_time = datetime.fromtimestamp(os.path.getmtime(log_path))
        date_str = file_time.strftime("%Y%m%d")
        
        # Get base name without extension
        base_dir = os.path.dirname(log_path)
        base_name = os.path.splitext(os.path.basename(log_path))[0]
        
        # Find next available revision number for today
        revision = 1
        while True:
            new_name = f"{base_name}_{date_str}_{revision:02d}.log"
            new_path = os.path.join(base_dir, new_name)
            if not os.path.exists(new_path):
                break
            revision += 1
        
        # Rename old log
        try:
            os.rename(log_path, new_path)
            print(f"Rotated log: {os.path.basename(log_path)} -> {os.path.basename(new_path)}")
        except Exception as e:
            print(f"Warning: Could not rotate log {log_path}: {e}")


def write_startup_log(message: str, base_path: str = None):
    """Write to startup log. If base_path not provided, tries to load from config."""
    global STARTUP_LOG
    
    try:
        # If base_path not provided, try to load from config
        if base_path is None:
            if STARTUP_LOG is None:
                # Try to get base_path from config
                if os.path.exists(CONFIG_FILE):
                    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                        config = json.load(f)
                        base_path = config.get("base_path")
                
                if base_path:
                    STARTUP_LOG = get_startup_log_path(base_path)
                else:
                    # Fallback to local logs if no config
                    local_log_dir = "logs"
                    os.makedirs(local_log_dir, exist_ok=True)
                    STARTUP_LOG = os.path.join(local_log_dir, "app_startup.log")
        else:
            STARTUP_LOG = get_startup_log_path(base_path)
        
        _rotate_log_if_needed(STARTUP_LOG)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(STARTUP_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {message}")
    except Exception as e:
        # Print to console if logging fails
        print(f"Warning: Could not write to startup log: {e}")


class TeeLogger:
    def __init__(self, q: queue.Queue, logfile_path: str):
        self.q = q
        self.logfile_path = logfile_path
        os.makedirs(os.path.dirname(self.logfile_path), exist_ok=True)
        # Rotate log before starting new operation
        _rotate_log_if_needed(self.logfile_path)

    def write(self, s):
        if not s:
            return
        self.q.put(s)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.logfile_path, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {s}")

    def flush(self):
        pass


# ---------- CONFIG STORAGE ----------

CONFIG_FILE = "yt_playlist_gui_config.json"

default_config = {
    "base_path": tools.BASE_DOWNLOAD_PATH,
    "playlists": [],
}


def load_config():
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


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


# ---------- PLAYLIST STATS (LOCAL / AVAILABLE / UNAVAILABLE) ----------

def get_playlist_stats(base_path: str, title: str, url: str, excluded_ids: list[str]) -> tuple[int, int, int]:
    """Compute local_count, available_count, unavailable_count for a playlist."""
    safe_title = tools._sanitize_title(title)
    playlist_folder = os.path.join(base_path, safe_title)

    local_count = 0
    if os.path.isdir(playlist_folder):
        video_exts = ("*.mp4", "*.mkv", "*.webm", "*.m4v")
        files = []
        for pat in video_exts:
            files.extend(glob(os.path.join(playlist_folder, pat)))
        local_count = len(files)

    available_count = 0
    unavailable_count = 0
    excluded_set = set(excluded_ids or [])

    try:
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "extract_flat": "in_playlist",
            "ignoreerrors": True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        entries = info.get("entries") or []

        for e in entries:
            if tools.is_entry_unavailable(e, excluded_set):
                unavailable_count += 1
            else:
                available_count += 1
    except Exception as ex:
        write_startup_log(f"Error getting playlist stats for {url}: {ex}\n")
        available_count = 0
        unavailable_count = 0

    return local_count, available_count, unavailable_count


# ---------- MAIN APP ----------

class PlaylistManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Playlist Manager")
        self.geometry("1200x650")

        self.config_data = load_config()
        self.log_queue = queue.Queue()
        self.worker = None
        self.is_working = False

        self.total_items = 0
        self.current_item_index = 0
        self.cancel_requested = False

        # Initialize startup log with base_path from config
        base_path = self.config_data.get("base_path")
        write_startup_log("=== App startup ===\n", base_path)
        self._refresh_all_playlist_stats_from_disk()

        self._build_ui()
        self._refresh_playlist_table()
        self.after(100, self._poll_log_queue)

    # ---------- UI BUILD ----------

    def _build_ui(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=8)

        left_frame = ttk.Frame(top_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))

        ttk.Label(left_frame, text="Base download path:").pack(anchor=tk.W)

        base_row = ttk.Frame(left_frame)
        base_row.pack(fill=tk.X, pady=(0, 6))

        self.base_path_var = tk.StringVar(value=self.config_data["base_path"])
        base_entry = ttk.Entry(base_row, textvariable=self.base_path_var, width=45)
        base_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(base_row, text="Browse...", command=self._choose_base_path).pack(
            side=tk.LEFT, padx=(4, 0)
        )

        ttk.Button(left_frame, text="Save Base Path",
                   command=self._save_base_path).pack(anchor=tk.W, pady=(0, 12))

        ttk.Label(left_frame, text="Playlists:").pack(anchor=tk.W)

        ttk.Button(left_frame, text="Add playlist",
                   command=self._add_playlist_dialog).pack(fill=tk.X, pady=(4, 2))

        ttk.Button(left_frame, text="Remove selected",
                   command=self._remove_selected_playlist).pack(fill=tk.X, pady=(0, 4))

        ttk.Button(left_frame, text="Edit exclusions for selected",
                   command=self._edit_exclusions_dialog).pack(fill=tk.X, pady=(0, 4))
        
        ttk.Button(left_frame, text="Fix folder structure for all",
                   command=self._fix_all_folder_structures).pack(fill=tk.X, pady=(0, 12))

        # Right: table
        right_frame = ttk.Frame(top_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        columns = ("title", "last_dl", "last_ex", "local", "plist", "unavail", "url")
        self.tree = ttk.Treeview(
            right_frame, columns=columns, show="headings", selectmode="browse"
        )

        self.tree.heading("title", text="Playlist")
        self.tree.heading("last_dl", text="Last download")
        self.tree.heading("last_ex", text="Last extract")
        self.tree.heading("local", text="Local videos")
        self.tree.heading("plist", text="Playlist videos")
        self.tree.heading("unavail", text="Unavailable")
        self.tree.heading("url", text="URL")

        self.tree.column("title", width=230, anchor=tk.W)
        self.tree.column("last_dl", width=140, anchor=tk.CENTER)
        self.tree.column("last_ex", width=140, anchor=tk.CENTER)
        self.tree.column("local", width=90, anchor=tk.E)
        self.tree.column("plist", width=100, anchor=tk.E)
        self.tree.column("unavail", width=100, anchor=tk.E)
        self.tree.column("url", width=320, anchor=tk.W)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tree_scroll = ttk.Scrollbar(
            right_frame, orient="vertical", command=self.tree.yview
        )
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        style = ttk.Style(self)
        style.configure("Treeview", rowheight=22)
        self.tree.tag_configure("needs_update", background="#ffcccc")

        self.tree.bind("<Double-1>", self._on_tree_double_click)

        action_frame = ttk.Frame(right_frame)
        action_frame.pack(side=tk.TOP, fill=tk.X, pady=(8, 0))

        ttk.Button(action_frame, text="Run on selected playlist",
                   command=self._run_on_selected).pack(side=tk.LEFT)

        ttk.Button(action_frame, text="Stop current task",
                   command=self._request_cancel).pack(side=tk.LEFT, padx=(8, 0))

        # Bottom: log + progress
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=False, padx=8, pady=(0, 8))

        ttk.Label(bottom_frame, text="Log:").pack(anchor=tk.W)

        log_text_frame = ttk.Frame(bottom_frame)
        log_text_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(log_text_frame, height=12, wrap="word", state=tk.DISABLED)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sb = ttk.Scrollbar(log_text_frame, orient="vertical", command=self.log_text.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=sb.set)

        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(
            bottom_frame, maximum=100.0, variable=self.progress_var
        )
        self.progress_bar.pack(fill=tk.X, pady=(4, 0))

    # ---------- CONFIG / PATHS ----------

    def _choose_base_path(self):
        path = filedialog.askdirectory(initialdir=self.base_path_var.get() or os.getcwd())
        if path:
            self.base_path_var.set(path)

    def _save_base_path(self):
        new_path = self.base_path_var.get().strip()
        if not new_path:
            messagebox.showerror("Error", "Base path cannot be empty.")
            return
        self.config_data["base_path"] = new_path
        save_config(self.config_data)
        tools.BASE_DOWNLOAD_PATH = new_path
        messagebox.showinfo("Saved", f"Base path set to:\n{new_path}")

    # ---------- TABLE ----------

    def _refresh_playlist_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for idx, pl in enumerate(self.config_data["playlists"]):
            title = pl.get("title", "")
            last_dl = pl.get("last_download_ist", "")
            last_ex = pl.get("last_extract_ist", "")
            local = pl.get("local_count", 0)
            plist = pl.get("playlist_count", 0)
            unavail = pl.get("unavailable_count", 0)
            url = pl.get("url", "")

            row_id = self.tree.insert(
                "",
                tk.END,
                iid=str(idx),
                values=(title, last_dl, last_ex, local, plist, unavail, url),
            )
            if plist != 0 and local != plist:
                self.tree.item(row_id, tags=("needs_update",))

    # ---------- STARTUP STATS ----------

    def _process_single_playlist_startup(self, pl: dict, base_path: str) -> dict:
        """Process a single playlist during startup (for parallel execution)."""
        import threading
        
        thread_id = threading.current_thread().name
        url = pl.get("url", "")
        title = pl.get("title", "")
        
        if not url or not title:
            return pl
        
        log_messages = []
        
        # Ensure folder structure exists for existing playlists
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_messages.append(f"[{timestamp}] [{thread_id}] [{title}] Checking folder structure")
            playlist_folder, archive_file, audio_folder = tools._build_playlist_paths(title, create_folders=True)
            
            # Check if playlist_info.json exists in snapshot directory
            snapshot_dir = os.path.join(playlist_folder, "playlist_info_snapshot")
            info_file = os.path.join(snapshot_dir, "playlist_info.json")
            
            if not os.path.exists(info_file):
                log_messages.append(f"[{timestamp}] [{thread_id}] [{title}] Creating missing playlist_info.json")
                
                # Try to save playlist_info.json if we can fetch it
                try:
                    entries = tools._get_playlist_entries(url, playlist_folder)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    log_messages.append(f"[{timestamp}] [{thread_id}] [{title}] ✓ Saved playlist_info.json with {len(entries)} entries")
                except Exception as e:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    log_messages.append(f"[{timestamp}] [{thread_id}] [{title}] ⚠️  Could not save playlist_info.json: {e}")
            else:
                log_messages.append(f"[{timestamp}] [{thread_id}] [{title}] ✓ playlist_info.json exists")
                    
        except Exception as e:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_messages.append(f"[{timestamp}] [{thread_id}] [{title}] ⚠️  Could not create folder structure: {e}")

        # Get stats
        excluded_ids = pl.get("excluded_ids", [])
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_messages.append(f"[{timestamp}] [{thread_id}] [{title}] Refreshing stats...")
        
        try:
            local_count, avail_count, unavail_count = get_playlist_stats(base_path, title, url, excluded_ids)
            pl["local_count"] = local_count
            pl["playlist_count"] = avail_count
            pl["unavailable_count"] = unavail_count
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_messages.append(f"[{timestamp}] [{thread_id}] [{title}] ✓ Stats: {local_count} local, {avail_count} available, {unavail_count} unavailable")
        except Exception as e:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_messages.append(f"[{timestamp}] [{thread_id}] [{title}] ⚠️  Error getting stats: {e}")
            pl["local_count"] = 0
            pl["playlist_count"] = 0
            pl["unavailable_count"] = 0

        if not pl.get("last_download_ist") or not pl.get("last_extract_ist"):
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pl.setdefault("last_download_ist", now_str)
            pl.setdefault("last_extract_ist", now_str)
        
        # Write all log messages for this playlist
        for msg in log_messages:
            write_startup_log(msg + "\n")
        
        return pl

    def _refresh_all_playlist_stats_from_disk(self):
        base_path = self.config_data["base_path"]
        playlists = self.config_data["playlists"]
        
        if not playlists:
            return
        
        write_startup_log(f"Starting parallel refresh of {len(playlists)} playlists...\n")
        start_time = datetime.now()
        
        # Use ThreadPoolExecutor for parallel processing
        # Limit to 5 concurrent threads to avoid overwhelming YouTube API
        max_workers = min(5, len(playlists))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all playlist processing tasks
            future_to_idx = {
                executor.submit(self._process_single_playlist_startup, pl, base_path): idx
                for idx, pl in enumerate(playlists)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    updated_pl = future.result()
                    self.config_data["playlists"][idx] = updated_pl
                except Exception as e:
                    write_startup_log(f"⚠️  Error processing playlist {playlists[idx].get('title', 'Unknown')}: {e}\n")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        write_startup_log(f"\n✓ Completed refresh of {len(playlists)} playlists in {duration:.1f} seconds\n")
        
        save_config(self.config_data)

    # ---------- PLAYLIST MANAGEMENT ----------

    def _add_playlist_dialog(self):
        url = simpledialog.askstring("Add playlist", "Enter YouTube playlist URL:")
        if not url:
            return

        self._append_log(f"\nFetching title for playlist:\n{url}\n")
        try:
            title = tools._get_playlist_info_title(url)
        except Exception as e:
            self._append_log(f"Could not fetch title automatically ({e}), using URL as title.\n")
            title = url

        base_path = self.config_data["base_path"]
        
        # Create playlist folder immediately
        try:
            playlist_folder, archive_file, audio_folder = tools._build_playlist_paths(title, create_folders=True)
            self._append_log(f"Created playlist folder: {playlist_folder}\n")
            
            # Save playlist_info.json immediately
            try:
                entries = tools._get_playlist_entries(url, playlist_folder)
                self._append_log(f"Saved playlist_info.json with {len(entries)} entries\n")
            except Exception as e:
                self._append_log(f"Warning: Could not save playlist_info.json: {e}\n")
        except Exception as e:
            self._append_log(f"Warning: Could not create playlist folder: {e}\n")
        
        local_count, avail_count, unavail_count = get_playlist_stats(base_path, title, url, [])

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        new_pl = {
            "url": url,
            "title": title,
            "last_download_ist": now_str,
            "last_extract_ist": now_str,
            "local_count": local_count,
            "playlist_count": avail_count,
            "unavailable_count": unavail_count,
            "excluded_ids": [],
        }

        self.config_data["playlists"].append(new_pl)
        save_config(self.config_data)
        self._refresh_playlist_table()
        self._append_log(
            f"Added playlist: {title}\n"
            f"Local videos: {local_count}\n"
            f"Downloadable in playlist: {avail_count}\n"
            f"Unavailable in playlist: {unavail_count}\n"
        )

    def _remove_selected_playlist(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Please select a playlist to remove.")
            return
        idx = int(sel[0])
        pl = self.config_data["playlists"][idx]
        if not messagebox.askyesno("Confirm", f"Remove playlist:\n{pl.get('title')} ?"):
            return
        del self.config_data["playlists"][idx]
        save_config(self.config_data)
        self._refresh_playlist_table()
        self._append_log(f"Removed playlist: {pl.get('title')}\n")

    def _edit_exclusions_dialog(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Please select a playlist.")
            return
        idx = int(sel[0])
        pl = self.config_data["playlists"][idx]
        current_ids = pl.get("excluded_ids", [])

        initial_text = "\n".join(current_ids)
        text = simpledialog.askstring(
            "Edit excluded IDs",
            f"Enter video IDs to treat as unavailable for:\n{pl.get('title')}\n\n"
            "One ID per line (or separated by spaces/commas):",
            initialvalue=initial_text,
        )
        if text is None:
            return

        raw = text.replace(",", " ").replace("\r", " ")
        ids = [t.strip() for t in raw.split() if t.strip()]
        pl["excluded_ids"] = sorted(set(ids))
        save_config(self.config_data)

        base_path = self.config_data["base_path"]
        url = pl.get("url", "")
        title = pl.get("title", "")
        local_count, avail_count, unavail_count = get_playlist_stats(base_path, title, url, pl["excluded_ids"])
        pl["local_count"] = local_count
        pl["playlist_count"] = avail_count
        pl["unavailable_count"] = unavail_count
        save_config(self.config_data)
        self._refresh_playlist_table()
        self._append_log(
            f"\nUpdated exclusions for {title}.\n"
            f"Excluded IDs: {', '.join(pl['excluded_ids'])}\n"
        )

    def _fix_all_folder_structures(self):
        """Manually fix folder structures for all playlists."""
        if not messagebox.askyesno(
            "Fix Folder Structures",
            "This will create missing folders and playlist_info_snapshot directories for all playlists.\n\n"
            "Continue?"
        ):
            return
        
        self._append_log("\n=== Fixing folder structures for all playlists ===\n")
        base_path = self.config_data["base_path"]
        fixed_count = 0
        
        for pl in self.config_data["playlists"]:
            url = pl.get("url", "")
            title = pl.get("title", "")
            if not url or not title:
                continue
            
            try:
                self._append_log(f"\nChecking: {title}\n")
                
                # Create folder structure
                playlist_folder, archive_file, audio_folder = tools._build_playlist_paths(title, create_folders=True)
                
                # Check if playlist_info_snapshot exists
                snapshot_dir = os.path.join(playlist_folder, "playlist_info_snapshot")
                info_file = os.path.join(snapshot_dir, "playlist_info.json")
                
                if not os.path.exists(info_file):
                    self._append_log(f"  Creating playlist_info_snapshot and fetching playlist info...\n")
                    try:
                        entries = tools._get_playlist_entries(url, playlist_folder)
                        self._append_log(f"  ✓ Saved playlist_info.json with {len(entries)} entries\n")
                        fixed_count += 1
                    except Exception as e:
                        self._append_log(f"  ⚠️  Could not fetch playlist info: {e}\n")
                else:
                    self._append_log(f"  ✓ Folder structure already complete\n")
                    
            except Exception as e:
                self._append_log(f"  ❌ Error: {e}\n")
        
        self._append_log(f"\n=== Fixed {fixed_count} playlist(s) ===\n")
        messagebox.showinfo("Complete", f"Fixed folder structures for {fixed_count} playlist(s).")

    # ---------- RUN MODES ----------

    def _on_tree_double_click(self, event):
        self._run_on_selected()

    def _run_on_selected(self):
        if self.is_working:
            messagebox.showinfo("Busy", "A task is already running.")
            return

        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Please select a playlist.")
            return
        idx = int(sel[0])
        pl = self.config_data["playlists"][idx]
        url = pl.get("url")
        title = pl.get("title")

        mode = self._ask_mode()
        if not mode:
            return

        self.progress_var.set(0.0)
        self.total_items = 0
        self.current_item_index = 0
        self._clear_log()
        self._append_log(
            f"Selected playlist: {title}\nURL: {url}\nMode: {mode}\n\n"
        )

        self.is_working = True
        self.worker = threading.Thread(
            target=self._run_mode_worker,
            args=(idx, mode, url, title),
            daemon=True,
        )
        self.worker.start()

    def _ask_mode(self) -> str | None:
        dlg = tk.Toplevel(self)
        dlg.title("Select mode")
        dlg.transient(self)
        dlg.grab_set()

        choice = tk.StringVar(value="")

        ttk.Label(dlg, text="Choose what to do for this playlist:").pack(
            padx=12, pady=(12, 6)
        )

        def set_choice(val):
            choice.set(val)
            dlg.destroy()

        ttk.Button(
            dlg,
            text="1 - Download video + extract audio (MP3)",
            command=lambda: set_choice("download_extract"),
        ).pack(fill=tk.X, padx=12, pady=4)

        ttk.Button(
            dlg,
            text="2 - Extract audio only (already downloaded)",
            command=lambda: set_choice("extract_only"),
        ).pack(fill=tk.X, padx=12, pady=(0, 12))

        dlg.wait_window()
        val = choice.get()
        return val or None

    def _request_cancel(self):
        if not self.is_working:
            messagebox.showinfo("No task", "No task is currently running.")
            return
        self.cancel_requested = True
        self._append_log("\nCancellation requested. Waiting for current step to finish...\n")

    def _run_mode_worker(self, index: int, mode: str, url: str, title: str):
        import sys

        base_path = self.config_data["base_path"]
        playlist_log = get_playlist_log_path(base_path, title)

        old_stdout = sys.stdout
        old_stderr = sys.stderr
        qlog = TeeLogger(self.log_queue, playlist_log)
        sys.stdout = qlog
        sys.stderr = qlog

        tools.BASE_DOWNLOAD_PATH = self.config_data["base_path"]

        runstate = SimpleNamespace(cancelled=False)

        def progress_cb(total, current_index):
            self.total_items = total
            self.current_item_index = current_index
            if self.cancel_requested or runstate.cancelled:
                raise KeyboardInterrupt("User requested cancellation")

        tools.GLOBAL_PROGRESS_CALLBACK = progress_cb
        tools.GLOBAL_RUNSTATE = runstate

        self.cancel_requested = False
        failed_ids = set()

        try:
            # Get excluded_ids from playlist config
            playlist_cfg = self._get_playlist_config(url)
            excluded_ids = set(playlist_cfg.get("excluded_ids", [])) if playlist_cfg else set()
            
            if mode == "download_extract":
                failed_ids = tools.download_playlist_with_video_and_audio(url, as_mp3=True, excluded_ids=excluded_ids)
                
                # Check if cancelled before continuing
                if not runstate.cancelled and not self.cancel_requested:
                    self._merge_failed_ids_into_playlist(index, failed_ids)
                    self._update_playlist_stats_from_disk(index, url, title, updated_download=True)
                else:
                    print("\n❌ Download cancelled by user.\n")
                    
            elif mode == "extract_only":
                tools.extract_audio_for_existing_playlist(title)
                
                # Check if cancelled before updating stats
                if not runstate.cancelled and not self.cancel_requested:
                    self._update_playlist_stats_from_disk(index, url, title, updated_extract=True)
                else:
                    print("\n❌ Extraction cancelled by user.\n")
            else:
                print(f"Unknown mode: {mode}")
                
        except KeyboardInterrupt as e:
            print(f"\n❌ Task cancelled: {e}\n")
        except Exception as e:
            print(f"\n❌ ERROR in worker: {e}\n")
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            self.log_queue.put("\n✓ Task ended.\n")
            self.is_working = False
            tools.GLOBAL_RUNSTATE = None
            self.progress_var.set(100.0)
            self._refresh_playlist_table()

    def _merge_failed_ids_into_playlist(self, index: int, failed_ids: set[str]):
        if not failed_ids:
            print(f"DEBUG: No failed IDs to merge")
            return
        pl = self.config_data["playlists"][index]
        existing = set(pl.get("excluded_ids", []))
        print(f"DEBUG: Existing excluded_ids: {existing}")
        print(f"DEBUG: New failed_ids: {failed_ids}")
        new_set = sorted(existing.union(failed_ids))
        print(f"DEBUG: Final excluded_ids: {new_set}")
        pl["excluded_ids"] = new_set
        save_config(self.config_data)
        self._append_log(
            f"\nMarked {len(failed_ids)} IDs as unavailable for this playlist:\n"
            + ", ".join(sorted(failed_ids)) + "\n"
        )

    # ---------- STATS UPDATE AFTER RUN ----------

    def _update_playlist_stats_from_disk(
        self,
        index: int,
        url: str,
        title: str,
        updated_download: bool = False,
        updated_extract: bool = False,
    ):
        base_path = self.config_data["base_path"]
        pl = self.config_data["playlists"][index]
        excluded_ids = pl.get("excluded_ids", [])
        local_count, avail_count, unavail_count = get_playlist_stats(base_path, title, url, excluded_ids)

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        pl["local_count"] = local_count
        pl["playlist_count"] = avail_count
        pl["unavailable_count"] = unavail_count

        if updated_download:
            pl["last_download_ist"] = now_str
        if updated_extract:
            pl["last_extract_ist"] = now_str

        save_config(self.config_data)

    # ---------- LOG + PROGRESS LOOP ----------

    def _append_log(self, text: str):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, text)
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _clear_log(self):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _poll_log_queue(self):
        try:
            while True:
                s = self.log_queue.get_nowait()
                self._append_log(s)
        except queue.Empty:
            pass

        if self.total_items > 0:
            pct = min(100.0, max(0.0, 100.0 * self.current_item_index / self.total_items))
            self.progress_var.set(pct)

        if getattr(self, "cancel_requested", False):
            rs = getattr(tools, "GLOBAL_RUNSTATE", None)
            if rs is not None:
                rs.cancelled = True

        self.after(100, self._poll_log_queue)

    def _get_playlist_config(self, url: str) -> dict | None:
        """Get playlist config from config_data by URL."""
        for playlist in self.config_data.get("playlists", []):
            if playlist.get("url") == url:
                return playlist
        return None


if __name__ == "__main__":
    #python yt_playlist_manager_gui_final.py
    app = PlaylistManagerApp()
    app.mainloop()
