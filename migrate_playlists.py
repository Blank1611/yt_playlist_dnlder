"""
Simple migration script to import playlists from Tkinter app to web backend
Run from project root: python migrate_playlists.py
"""
import json
import sys
import os
from datetime import datetime
from pathlib import Path as PathLib

# Change to backend directory so database is created in correct location
backend_dir = PathLib(__file__).parent / "yt_serve" / "backend"
os.chdir(str(backend_dir))

# Add backend to path
sys.path.insert(0, str(backend_dir))

# Load environment
from dotenv import load_dotenv
load_dotenv(".env")

from app.models.database import SessionLocal, Playlist
from app.core.config import settings

def parse_ist_datetime(ist_str: str):
    """Parse IST datetime string"""
    if not ist_str:
        return None
    try:
        return datetime.strptime(ist_str, "%Y-%m-%d %H:%M:%S")
    except:
        return None

def main():
    """Run migration"""
    # Config file is in project root, we're now in backend dir
    config_file = "../../yt_playlist_gui_config.json"
    
    if not PathLib(config_file).exists():
        print(f"❌ Config file not found: {config_file}")
        print("   Make sure yt_playlist_gui_config.json exists in project root")
        return
    
    # Load config
    print("="*60)
    print("MIGRATION: Tkinter → Web Backend")
    print("="*60)
    print(f"\nLoading: {config_file}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    old_path = config.get('base_path', '')
    new_path = settings.BASE_DOWNLOAD_PATH
    
    print(f"\nOld base path: {old_path}")
    print(f"New base path: {new_path}")
    
    # Normalize paths for comparison
    old_normalized = os.path.normpath(old_path)
    new_normalized = os.path.normpath(new_path)
    
    if old_normalized != new_normalized:
        print("\n⚠️  WARNING: Base paths don't match!")
        print(f"   Old (normalized): {old_normalized}")
        print(f"   New (normalized): {new_normalized}")
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled")
            return
    
    # Get database
    db = SessionLocal()
    
    try:
        playlists = config.get('playlists', [])
        print(f"\nFound {len(playlists)} playlists to migrate")
        print()
        
        added = 0
        updated = 0
        
        for p in playlists:
            url = p['url']
            existing = db.query(Playlist).filter(Playlist.url == url).first()
            
            if existing:
                print(f"📝 Updating: {p['title']}")
                existing.title = p['title']
                existing.local_count = p.get('local_count', 0)
                existing.playlist_count = p.get('playlist_count', 0)
                existing.unavailable_count = p.get('unavailable_count', 0)
                existing.excluded_ids = p.get('excluded_ids', [])
                
                last_dl = parse_ist_datetime(p.get('last_download_ist'))
                last_ex = parse_ist_datetime(p.get('last_extract_ist'))
                if last_dl:
                    existing.last_download = last_dl
                if last_ex:
                    existing.last_extract = last_ex
                
                existing.updated_at = datetime.utcnow()
                updated += 1
            else:
                print(f"✅ Adding: {p['title']}")
                new_pl = Playlist(
                    url=url,
                    title=p['title'],
                    local_count=p.get('local_count', 0),
                    playlist_count=p.get('playlist_count', 0),
                    unavailable_count=p.get('unavailable_count', 0),
                    excluded_ids=p.get('excluded_ids', []),
                    last_download=parse_ist_datetime(p.get('last_download_ist')),
                    last_extract=parse_ist_datetime(p.get('last_extract_ist'))
                )
                db.add(new_pl)
                added += 1
            
            print(f"   Local: {p.get('local_count', 0)}, "
                  f"Playlist: {p.get('playlist_count', 0)}, "
                  f"Excluded: {len(p.get('excluded_ids', []))}")
        
        db.commit()
        
        print("\n" + "="*60)
        print("✅ MIGRATION COMPLETE")
        print("="*60)
        print(f"Added: {added}")
        print(f"Updated: {updated}")
        print(f"Total: {added + updated}")
        print("\n📋 Next: Start backend with 'python yt_serve/backend/run.py'")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
