"""
Migration script to import playlists and config from Tkinter app
"""
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app.models.database import SessionLocal, Playlist

# Load settings manually to ensure .env is read
from dotenv import load_dotenv
load_dotenv()

from app.core.config import settings

def parse_ist_datetime(ist_str: str) -> datetime:
    """Parse IST datetime string to UTC datetime"""
    if not ist_str:
        return None
    
    try:
        # Parse IST datetime
        dt = datetime.strptime(ist_str, "%Y-%m-%d %H:%M:%S")
        # Note: Not converting timezone, just storing as-is
        # You can add timezone conversion if needed
        return dt
    except:
        return None

def migrate_config(config_path: str):
    """
    Migrate playlists and config from Tkinter app
    
    Args:
        config_path: Path to yt_playlist_gui_config.json
    """
    # Load existing config
    print(f"Loading config from: {config_path}")
    with open(config_path, 'r', encoding='utf-8') as f:
        old_config = json.load(f)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Check base path
        old_base_path = old_config.get('base_path', '')
        current_base_path = settings.BASE_DOWNLOAD_PATH
        
        print(f"\nOld base path: {old_base_path}")
        print(f"Current base path: {current_base_path}")
        
        if old_base_path != current_base_path:
            print("\n⚠️  WARNING: Base paths don't match!")
            print("You may need to update BASE_DOWNLOAD_PATH in .env file")
            response = input("\nContinue anyway? (y/n): ")
            if response.lower() != 'y':
                print("Migration cancelled")
                return
        
        # Get existing playlists
        existing_playlists = db.query(Playlist).all()
        existing_urls = {p.url for p in existing_playlists}
        
        print(f"\nFound {len(existing_playlists)} existing playlists in database")
        print(f"Found {len(old_config['playlists'])} playlists in config file")
        
        # Migrate playlists
        added = 0
        updated = 0
        skipped = 0
        
        for old_playlist in old_config['playlists']:
            url = old_playlist['url']
            
            # Check if playlist already exists
            existing = db.query(Playlist).filter(Playlist.url == url).first()
            
            if existing:
                # Update existing playlist
                print(f"\n📝 Updating: {old_playlist['title']}")
                
                existing.title = old_playlist['title']
                existing.local_count = old_playlist.get('local_count', 0)
                existing.playlist_count = old_playlist.get('playlist_count', 0)
                existing.unavailable_count = old_playlist.get('unavailable_count', 0)
                existing.excluded_ids = old_playlist.get('excluded_ids', [])
                
                # Parse dates
                last_download = parse_ist_datetime(old_playlist.get('last_download_ist'))
                last_extract = parse_ist_datetime(old_playlist.get('last_extract_ist'))
                
                if last_download:
                    existing.last_download = last_download
                if last_extract:
                    existing.last_extract = last_extract
                
                existing.updated_at = datetime.utcnow()
                
                updated += 1
            else:
                # Add new playlist
                print(f"\n✅ Adding: {old_playlist['title']}")
                
                new_playlist = Playlist(
                    url=url,
                    title=old_playlist['title'],
                    local_count=old_playlist.get('local_count', 0),
                    playlist_count=old_playlist.get('playlist_count', 0),
                    unavailable_count=old_playlist.get('unavailable_count', 0),
                    excluded_ids=old_playlist.get('excluded_ids', []),
                    last_download=parse_ist_datetime(old_playlist.get('last_download_ist')),
                    last_extract=parse_ist_datetime(old_playlist.get('last_extract_ist')),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                db.add(new_playlist)
                added += 1
            
            # Show details
            print(f"   URL: {url}")
            print(f"   Local: {old_playlist.get('local_count', 0)}, "
                  f"Playlist: {old_playlist.get('playlist_count', 0)}, "
                  f"Unavailable: {old_playlist.get('unavailable_count', 0)}")
            print(f"   Excluded IDs: {len(old_playlist.get('excluded_ids', []))}")
        
        # Commit changes
        db.commit()
        
        # Summary
        print("\n" + "="*60)
        print("MIGRATION COMPLETE")
        print("="*60)
        print(f"✅ Added: {added} playlists")
        print(f"📝 Updated: {updated} playlists")
        print(f"⏭️  Skipped: {skipped} playlists")
        print(f"📊 Total: {added + updated + skipped} playlists")
        print("="*60)
        
        # Show next steps
        print("\n📋 Next Steps:")
        print("1. Start the backend: python run.py")
        print("2. Open API docs: http://localhost:8000/docs")
        print("3. View playlists: GET /api/playlists")
        print("4. Start downloads: POST /api/downloads/jobs")
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()

if __name__ == "__main__":
    # Default config path (relative to project root)
    default_config = "../../yt_playlist_gui_config.json"
    
    # Get config path from command line or use default
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        # Try to find config in parent directories
        current_dir = Path(__file__).parent
        config_path = current_dir.parent.parent / "yt_playlist_gui_config.json"
        
        if not config_path.exists():
            print("❌ Config file not found!")
            print(f"   Looked in: {config_path}")
            print("\nUsage:")
            print("   python migrate_from_tkinter.py [path/to/yt_playlist_gui_config.json]")
            sys.exit(1)
    
    # Check if config exists
    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        sys.exit(1)
    
    # Run migration
    print("="*60)
    print("TKINTER APP → WEB BACKEND MIGRATION")
    print("="*60)
    
    migrate_config(str(config_path))
