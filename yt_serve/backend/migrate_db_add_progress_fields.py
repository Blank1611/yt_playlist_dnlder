"""
Database migration: Add separate download/extract progress fields to jobs table
"""
import sqlite3
from pathlib import Path

def migrate():
    db_path = Path(__file__).parent / "yt_manager.db"
    
    if not db_path.exists():
        print("Database doesn't exist yet, no migration needed")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(jobs)")
    columns = [row[1] for row in cursor.fetchall()]
    
    new_columns = [
        ("download_status", "TEXT"),
        ("download_total", "INTEGER DEFAULT 0"),
        ("download_completed", "INTEGER DEFAULT 0"),
        ("download_failed", "INTEGER DEFAULT 0"),
        ("download_batch_info", "TEXT"),
        ("extract_status", "TEXT"),
        ("extract_total", "INTEGER DEFAULT 0"),
        ("extract_completed", "INTEGER DEFAULT 0"),
        ("extract_failed", "INTEGER DEFAULT 0"),
    ]
    
    for col_name, col_type in new_columns:
        if col_name not in columns:
            print(f"Adding column: {col_name}")
            cursor.execute(f"ALTER TABLE jobs ADD COLUMN {col_name} {col_type}")
        else:
            print(f"Column {col_name} already exists, skipping")
    
    conn.commit()
    conn.close()
    
    print("✓ Migration complete!")

if __name__ == "__main__":
    migrate()
