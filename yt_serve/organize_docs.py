"""
Script to organize documentation into DOCS folder structure
"""
import os
import shutil
from pathlib import Path

# Create directory structure
docs_root = Path("DOCS")
dev_docs = docs_root / "developer-docs"
user_docs = docs_root / "end-user-docs"

# Create directories
docs_root.mkdir(exist_ok=True)
dev_docs.mkdir(exist_ok=True)
user_docs.mkdir(exist_ok=True)

# Developer documentation (from root)
dev_docs_root = [
    "DEVELOPER_GUIDE.md",
    "THREADING_ARCHITECTURE.md",
    "PARALLEL_OPERATIONS.md",
    "PARALLEL_LOGGING_GUIDE.md",
    "LOG_ROTATION_GUIDE.md",
    "STARTUP_CACHE_OPTIMIZATION.md",
    "UI_RESPONSIVENESS_FIX.md",
    "TRANSIENT_ERROR_FIX.md",
    "ERROR_CLASSIFICATION.md",
    "CRASH_RECOVERY.md",
    "CUSTOM_ARCHIVE_IMPROVEMENTS.md",
]

# End-user documentation (from root)
user_docs_root = [
    "END_USER_GUIDE.md",
    "AUDIO_VIDEO_QUALITY_GUIDE.md",
    "AUDIO_EXTRACTION_ERROR_HANDLING.md",
    "BATCH_DOWNLOAD_GUIDE.md",
    "CONFIG_SETUP.md",
    "EXCLUSIONS_EDITOR_GUIDE.md",
    "FOLDER_STRUCTURE.md",
    "INTERACTIVE_MATCHING_GUIDE.md",
    "OLD_FORMAT_AUTO_RENAME.md",
    "RENAME_SCRIPT_GUIDE.md",
    "RENAME_SCRIPT_TROUBLESHOOTING.md",
    "UNIFIED_DOWNLOAD_GUIDE.md",
]

# Developer documentation (from yt_serve)
dev_docs_ytserve = [
    "yt_serve/COMPLETE.md",
    "yt_serve/IMPLEMENTATION_STATUS.md",
    "yt_serve/LOGGING_ARCHITECTURE.md",
    "yt_serve/TESTING_GUIDE.md",
    "yt_serve/BROWSER_LIMITATIONS.md",
    "yt_serve/FRONTEND_COMPLETE.md",
    "yt_serve/EXCLUSIONS_FEATURE.md",
    "yt_serve/LATEST_IMPROVEMENTS.md",
    "yt_serve/UI_IMPROVEMENTS.md",
    "yt_serve/KNOWN_ISSUES.md",
]

# End-user documentation (from yt_serve)
user_docs_ytserve = [
    "yt_serve/GETTING_STARTED.md",
    "yt_serve/SETUP_GUIDE.md",
    "yt_serve/MIGRATION_GUIDE.md",
    "yt_serve/MIGRATION_SUCCESS.md",
    "yt_serve/TROUBLESHOOTING.md",
    "yt_serve/NODE_MODULES_EXPLAINED.md",
]

# Move files
print("Organizing documentation...")
print()

# Developer docs from root
print("Moving developer docs from root...")
for doc in dev_docs_root:
    if Path(doc).exists():
        dest = dev_docs / Path(doc).name
        shutil.copy2(doc, dest)
        print(f"  ✓ {doc} -> {dest}")

# User docs from root
print("\nMoving user docs from root...")
for doc in user_docs_root:
    if Path(doc).exists():
        dest = user_docs / Path(doc).name
        shutil.copy2(doc, dest)
        print(f"  ✓ {doc} -> {dest}")

# Developer docs from yt_serve
print("\nMoving developer docs from yt_serve...")
for doc in dev_docs_ytserve:
    if Path(doc).exists():
        dest = dev_docs / Path(doc).name
        shutil.copy2(doc, dest)
        print(f"  ✓ {doc} -> {dest}")

# User docs from yt_serve
print("\nMoving user docs from yt_serve...")
for doc in user_docs_ytserve:
    if Path(doc).exists():
        dest = user_docs / Path(doc).name
        shutil.copy2(doc, dest)
        print(f"  ✓ {doc} -> {dest}")

print("\n" + "="*60)
print("Documentation organized successfully!")
print("="*60)
print(f"\nStructure:")
print(f"  DOCS/")
print(f"    developer-docs/ ({len(list(dev_docs.glob('*.md')))} files)")
print(f"    end-user-docs/ ({len(list(user_docs.glob('*.md')))} files)")
print()
print("Note: Original files kept in place. Delete manually if needed.")
