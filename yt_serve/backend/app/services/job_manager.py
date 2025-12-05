"""
Job manager for background download/extract tasks
"""
import asyncio
import os
from typing import Dict, Optional, Callable
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.database import Job, Playlist
from app.services.ytdlp_service import DownloadService
from app.core.config import settings

class JobManager:
    """Manages background jobs"""
    
    def __init__(self):
        self.active_jobs: Dict[int, asyncio.Task] = {}
        self.cancel_flags: Dict[int, bool] = {}
        self.download_services: Dict[int, DownloadService] = {}  # Track services for cancellation
        
        # Ensure logs directory exists
        self.logs_dir = os.path.join(settings.BASE_DOWNLOAD_PATH, "logs")
        os.makedirs(self.logs_dir, exist_ok=True)
    
    def _get_log_file_path(self, job_id: int) -> str:
        """Get log file path for a job"""
        return os.path.join(self.logs_dir, f"job_{job_id}.log")
    
    def _write_log(self, job_id: int, message: str):
        """Write log message to file"""
        log_file = self._get_log_file_path(job_id)
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    
    async def create_download_job(
        self,
        db: Session,
        playlist_id: int,
        job_type: str,
        download_service: DownloadService,
        log_callback: Optional[Callable] = None,
        progress_callback: Optional[Callable] = None
    ) -> int:
        """
        Create and start a download job
        
        Args:
            db: Database session
            playlist_id: Playlist ID
            job_type: "download", "extract", or "both"
            download_service: Download service instance
            log_callback: Async function(job_id, message) for logs
            progress_callback: Async function(job_id, progress, completed, total) for progress
        
        Returns:
            Job ID
        """
        # Get playlist
        playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
        if not playlist:
            raise ValueError(f"Playlist {playlist_id} not found")
        
        # Create job
        job = Job(
            playlist_id=playlist_id,
            job_type=job_type,
            status="pending"
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Start job task
        task = asyncio.create_task(
            self._run_job(
                job.id,
                playlist,
                job_type,
                download_service,
                log_callback,
                progress_callback
            )
        )
        self.active_jobs[job.id] = task
        self.cancel_flags[job.id] = False
        self.download_services[job.id] = download_service  # Store for cancellation
        
        return job.id
    
    async def _run_job(
        self,
        job_id: int,
        playlist: Playlist,
        job_type: str,
        download_service: DownloadService,
        log_callback: Optional[Callable],
        progress_callback: Optional[Callable]
    ):
        """Run a job"""
        from app.models.database import SessionLocal
        db = SessionLocal()
        
        try:
            # Update job status
            job = db.query(Job).filter(Job.id == job_id).first()
            job.status = "running"
            job.started_at = datetime.utcnow()
            db.commit()
            
            # Log start
            if log_callback:
                await log_callback(job_id, f"Starting {job_type} for playlist: {playlist.title}")
            
            # Create progress wrapper
            async def progress_wrapper(total, current):
                if self.cancel_flags.get(job_id):
                    raise asyncio.CancelledError("Job cancelled")
                
                # Update job
                job = db.query(Job).filter(Job.id == job_id).first()
                job.total_items = total
                job.completed_items = current
                job.progress = (current / total * 100) if total > 0 else 0
                db.commit()
                
                # Callback
                if progress_callback:
                    await progress_callback(job_id, job.progress, current, total)
            
            # Create log wrapper
            async def log_wrapper(message):
                # Write to file
                self._write_log(job_id, message)
                
                # Send to WebSocket
                if log_callback:
                    await log_callback(job_id, message)
            
            # Execute job
            if job_type == "download" or job_type == "both":
                await log_wrapper("Starting download...")
                
                failed_ids = await download_service.download_playlist(
                    playlist.url,
                    set(playlist.excluded_ids or []),
                    progress_callback=progress_wrapper,
                    log_callback=log_wrapper
                )
                
                # Update playlist
                playlist.last_download = datetime.utcnow()
                
                # Add failed IDs to exclusions
                if failed_ids:
                    existing = set(playlist.excluded_ids or [])
                    playlist.excluded_ids = list(existing.union(failed_ids))
                
                db.commit()
                
                await log_wrapper(f"Download completed. Failed: {len(failed_ids)}")
            
            if job_type == "extract" or job_type == "both":
                await log_wrapper("Starting audio extraction...")
                
                await download_service.extract_audio(
                    playlist.title,
                    progress_callback=progress_wrapper,
                    log_callback=log_wrapper
                )
                
                # Update playlist
                playlist.last_extract = datetime.utcnow()
                db.commit()
                
                await log_wrapper("Audio extraction completed")
            
            # Update job status
            job = db.query(Job).filter(Job.id == job_id).first()
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            job.progress = 100.0
            db.commit()
            
            await log_wrapper("Job completed successfully")
            
        except asyncio.CancelledError:
            # Job was cancelled
            job = db.query(Job).filter(Job.id == job_id).first()
            job.status = "cancelled"
            job.completed_at = datetime.utcnow()
            db.commit()
            
            if log_callback:
                await log_callback(job_id, "Job cancelled by user")
        
        except Exception as e:
            # Job failed
            job = db.query(Job).filter(Job.id == job_id).first()
            job.status = "failed"
            job.error = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()
            
            if log_callback:
                await log_callback(job_id, f"Job failed: {str(e)}")
        
        finally:
            # Cleanup
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]
            if job_id in self.cancel_flags:
                del self.cancel_flags[job_id]
            if job_id in self.download_services:
                del self.download_services[job_id]
            
            db.close()
    
    async def cancel_job(self, job_id: int):
        """Cancel a running job"""
        if job_id in self.cancel_flags:
            self.cancel_flags[job_id] = True
        
        # Cancel the download service's current job
        if job_id in self.download_services:
            self.download_services[job_id].cancel_current_job()
        
        if job_id in self.active_jobs:
            task = self.active_jobs[job_id]
            task.cancel()
    
    def get_active_jobs(self) -> list:
        """Get list of active job IDs"""
        return list(self.active_jobs.keys())
    
    def get_job_logs(self, job_id: int, lines: Optional[int] = None) -> list:
        """
        Get job logs from file
        
        Args:
            job_id: Job ID
            lines: Number of lines to return (from end), None for all
        
        Returns:
            List of log lines
        """
        log_file = self._get_log_file_path(job_id)
        
        if not os.path.exists(log_file):
            return []
        
        with open(log_file, "r", encoding="utf-8") as f:
            all_lines = f.readlines()
        
        if lines is not None:
            return all_lines[-lines:]
        
        return all_lines

# Global job manager instance
job_manager = JobManager()
