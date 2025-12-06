@echo off
echo ========================================
echo YouTube Playlist Manager - Web Version
echo ========================================
echo.
echo Starting servers...
echo.

REM Start backend in new window
echo [1/2] Starting Backend (Python)...
start "YT Manager - Backend" cmd /k "cd yt_serve\backend && E:\laptop_stuff\Harry Potter\testyoutube\ytdld\Scripts\python.exe run.py"
timeout /t 3 /nobreak > nul

REM Start frontend in new window
echo [2/2] Starting Frontend (React)...
start "YT Manager - Frontend" cmd /k "cd yt_serve\frontend && npm run dev"

echo.
echo ========================================
echo Servers starting in separate windows!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit this window...
pause > nul
