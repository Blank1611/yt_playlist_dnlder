"""
FastAPI main application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio

from app.api import playlists, downloads, config, websocket
from app.core.config import settings

app = FastAPI(
    title="YouTube Playlist Manager API",
    description="Backend API for YouTube playlist management",
    version="2.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Refresh all playlist stats on server startup"""
    print("\n" + "="*60)
    print("Refreshing playlist stats on startup...")
    print("="*60)
    
    from app.models.database import SessionLocal, Playlist
    from app.services.ytdlp_service import DownloadService
    
    db = SessionLocal()
    try:
        playlists_list = db.query(Playlist).all()
        if not playlists_list:
            print("No playlists found")
            return
        
        print(f"Found {len(playlists_list)} playlists to refresh")
        
        download_service = DownloadService(settings.BASE_DOWNLOAD_PATH, {
            "audio_extract_mode": settings.AUDIO_EXTRACT_MODE,
            "max_extraction_workers": settings.MAX_CONCURRENT_EXTRACTIONS,
            "batch_size": settings.BATCH_SIZE,
            "use_browser_cookies": settings.USE_BROWSER_COOKIES,
            "browser_name": settings.BROWSER_NAME,
            "cookies_file": settings.COOKIES_FILE,
        })
        
        for playlist in playlists_list:
            try:
                print(f"  Refreshing: {playlist.title}...", end=" ")
                local_count, available_count, unavailable_count = await download_service.get_playlist_stats(
                    playlist.title,
                    playlist.url,
                    playlist.excluded_ids or []
                )
                
                playlist.local_count = local_count
                playlist.playlist_count = available_count
                playlist.unavailable_count = unavailable_count
                db.commit()
                
                status = "✓ Caught up" if local_count >= available_count else f"⚠ {available_count - local_count} new"
                print(f"{status} ({local_count}/{available_count})")
                
            except Exception as e:
                print(f"✗ Error: {str(e)}")
        
        print("="*60)
        print("Playlist refresh complete!")
        print("="*60 + "\n")
        
    finally:
        db.close()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(playlists.router, prefix="/api/playlists", tags=["playlists"])
app.include_router(downloads.router, prefix="/api/downloads", tags=["downloads"])
app.include_router(config.router, prefix="/api/config", tags=["config"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "YouTube Playlist Manager API",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
