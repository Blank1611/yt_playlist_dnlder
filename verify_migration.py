"""
Quick script to verify migration worked
"""
import sys
import os
from pathlib import Path

# Change to backend directory
backend_dir = Path(__file__).parent / "yt_serve" / "backend"
os.chdir(str(backend_dir))
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv(".env")

from app.models.database import SessionLocal, Playlist

def main():
    db = SessionLocal()
    
    try:
        playlists = db.query(Playlist).all()
        
        print("="*60)
        print("DATABASE VERIFICATION")
        print("="*60)
        print(f"\nDatabase location: {backend_dir / 'yt_manager.db'}")
        print(f"Total playlists: {len(playlists)}\n")
        
        if playlists:
            print("Playlists found:")
            for i, p in enumerate(playlists, 1):
                print(f"{i:2}. {p.title}")
                print(f"    Local: {p.local_count}, Playlist: {p.playlist_count}, Excluded: {len(p.excluded_ids or [])}")
            
            print("\n✅ Migration successful!")
            print("\nNext: Restart backend and test API")
            print("      http://localhost:8000/api/playlists")
        else:
            print("❌ No playlists found!")
            print("\nRun: python migrate_playlists.py")
    
    finally:
        db.close()

if __name__ == "__main__":
    main()
