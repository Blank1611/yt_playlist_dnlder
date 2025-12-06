@echo off
title YouTube Playlist Manager
color 0A

echo.
echo ========================================
echo   YouTube Playlist Manager
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed!
    echo.
    echo Please install Node.js from: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo [1/5] Checking Python installation... OK
echo [2/5] Checking Node.js installation... OK
echo.

REM Check if backend venv exists
if not exist "yt_serve\backend\venv" (
    echo [3/5] Setting up backend for first time...
    cd yt_serve\backend
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
    if not exist ".env" (
        copy .env.example .env
        echo.
        echo [!] Please edit yt_serve\backend\.env with your settings
        echo     Especially BASE_DOWNLOAD_PATH
        echo.
        pause
    )
    cd ..\..
) else (
    echo [3/5] Backend already set up... OK
)

REM Check if frontend node_modules exists
if not exist "yt_serve\frontend\node_modules" (
    echo [4/5] Setting up frontend for first time...
    echo     This may take 2-3 minutes...
    cd yt_serve\frontend
    call npm install
    cd ..\..
) else (
    echo [4/5] Frontend already set up... OK
)

echo [5/5] Starting servers...
echo.

REM Start backend in new window
start "YouTube Manager - Backend" cmd /k "cd yt_serve\backend && venv\Scripts\activate && python run.py"
timeout /t 3 /nobreak > nul

REM Start frontend in new window
start "YouTube Manager - Frontend" cmd /k "cd yt_serve\frontend && npm run dev"
timeout /t 3 /nobreak > nul

echo.
echo ========================================
echo   Application Starting!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Opening browser in 5 seconds...
timeout /t 5 /nobreak > nul

REM Open browser
start http://localhost:5173

echo.
echo Application is running!
echo.
echo To stop: Close the two server windows
echo          (YouTube Manager - Backend and Frontend)
echo.
pause
