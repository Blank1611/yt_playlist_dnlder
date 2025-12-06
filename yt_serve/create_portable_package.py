"""
Create a portable package for end users
No installation required - just extract and run
"""
import os
import shutil
import zipfile
from pathlib import Path

def create_portable():
    """Create portable package"""
    
    print("="*60)
    print("Creating Portable Package")
    print("="*60)
    print()
    
    # Create package directory
    package_dir = Path("YouTubePlaylistManager_Portable")
    if package_dir.exists():
        print("Removing old package...")
        shutil.rmtree(package_dir)
    
    package_dir.mkdir()
    print(f"✓ Created {package_dir}")
    
    # Copy essential files
    print("\nCopying files...")
    
    files_to_copy = [
        "LAUNCH_APP.bat",
        "README.md",
        "QUICKSTART.md",
        "LICENSE",
        "requirements.txt",
        "migrate_playlists.py",
        "verify_migration.py",
        "yt_playlist_audio_tools.py",
    ]
    
    for file in files_to_copy:
        if Path(file).exists():
            shutil.copy2(file, package_dir / file)
            print(f"  ✓ {file}")
    
    # Copy directories
    print("\nCopying directories...")
    
    dirs_to_copy = [
        "yt_serve",
        "DOCS",
    ]
    
    for dir_name in dirs_to_copy:
        if Path(dir_name).exists():
            shutil.copytree(dir_name, package_dir / dir_name, 
                          ignore=shutil.ignore_patterns(
                              '__pycache__', '*.pyc', 'node_modules', 
                              'venv', '.vite', 'dist', '*.db', '*.log'
                          ))
            print(f"  ✓ {dir_name}")
    
    # Create README for portable version
    portable_readme = """# YouTube Playlist Manager - Portable Version

## Quick Start

1. **Install Prerequisites** (one-time setup):
   - Python 3.8+: https://www.python.org/downloads/
   - Node.js 16+: https://nodejs.org/
   - Make sure to check "Add to PATH" during installation

2. **Run the Application**:
   - Double-click `LAUNCH_APP.bat`
   - First run will set up everything automatically (2-3 minutes)
   - Browser will open automatically

3. **Use the Application**:
   - Add playlists
   - Download videos
   - Extract audio
   - Enjoy!

## What's Included

- ✅ Complete application source code
- ✅ One-click launcher (LAUNCH_APP.bat)
- ✅ All documentation (DOCS folder)
- ✅ Migration tools

## First Run

The first time you run LAUNCH_APP.bat:
1. It will create a Python virtual environment
2. Install Python dependencies
3. Install Node.js dependencies
4. Create configuration file
5. Start the servers
6. Open your browser

This takes 2-3 minutes. Subsequent runs are instant!

## Configuration

Edit `yt_serve/backend/.env` to configure:
- Download path
- Audio quality
- Batch size
- And more...

## Documentation

See `DOCS/end-user-docs/` for complete guides.

## Troubleshooting

If you encounter issues:
1. Make sure Python and Node.js are installed
2. Check they're added to PATH
3. See `DOCS/end-user-docs/TROUBLESHOOTING.md`

## Support

- Documentation: DOCS/
- Issues: GitHub Issues
- Discussions: GitHub Discussions

---

**No installation required - just extract and run!**
"""
    
    (package_dir / "README_PORTABLE.txt").write_text(portable_readme)
    print("  ✓ README_PORTABLE.txt")
    
    # Create ZIP file
    print("\nCreating ZIP archive...")
    zip_name = "YouTubePlaylistManager_Portable.zip"
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            # Skip unwanted directories
            dirs[:] = [d for d in dirs if d not in 
                      ['__pycache__', 'node_modules', 'venv', '.vite', 'dist']]
            
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(package_dir.parent)
                zipf.write(file_path, arcname)
    
    # Get size
    size_mb = Path(zip_name).stat().st_size / (1024 * 1024)
    
    print()
    print("="*60)
    print("Portable Package Created!")
    print("="*60)
    print()
    print(f"Package: {zip_name}")
    print(f"Size: {size_mb:.1f} MB")
    print()
    print("To distribute:")
    print(f"1. Share {zip_name}")
    print("2. Users extract it")
    print("3. Users double-click LAUNCH_APP.bat")
    print("4. Done!")
    print()
    print("Note: Users still need Python and Node.js installed")
    print("      But no manual setup required!")
    print()

if __name__ == '__main__':
    create_portable()
