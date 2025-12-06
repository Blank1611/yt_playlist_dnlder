@echo off
setlocal enabledelayedexpansion

title YouTube Playlist Manager - Setup
color 0A

echo.
echo ========================================
echo   YouTube Playlist Manager Setup
echo ========================================
echo.
echo Installing dependencies...
echo This will take 2-3 minutes.
echo.

REM Get the directory where this script is located
set "APP_DIR=%~dp0"
cd /d "%APP_DIR%"

REM Use portable Python if available
if exist "portable\python\python.exe" (
    set "PYTHON_EXE=%APP_DIR%portable\python\python.exe"
    set "PIP_EXE=%APP_DIR%portable\python\Scripts\pip.exe"
    echo [1/4] Using bundled Python... OK
) else (
    set "PYTHON_EXE=python"
    set "PIP_EXE=pip"
    echo [1/4] Using system Python... OK
)

REM Use portable Node.js if available
if exist "portable\nodejs\node.exe" (
    set "NODE_EXE=%APP_DIR%portable\nodejs\node.exe"
    set "NPM_EXE=%APP_DIR%portable\nodejs\npm.cmd"
    set "PATH=%APP_DIR%portable\nodejs;%PATH%"
    echo [2/4] Using bundled Node.js... OK
) else (
    set "NODE_EXE=node"
    set "NPM_EXE=npm"
    echo [2/4] Using system Node.js... OK
)

REM Setup backend
echo [3/4] Setting up backend...
cd "%APP_DIR%yt_serve\backend"

if not exist "venv" (
    echo   Creating virtual environment...
    "%PYTHON_EXE%" -m venv venv
)

echo   Installing Python packages...
call venv\Scripts\activate
"%PIP_EXE%" install -r requirements.txt >nul 2>&1

if not exist ".env" (
    copy .env.example .env >nul
)

cd "%APP_DIR%"

REM Setup frontend
echo [4/4] Setting up frontend...
cd "%APP_DIR%yt_serve\frontend"

if not exist "node_modules" (
    echo   Installing Node packages (this may take 2-3 minutes)...
    call "%NPM_EXE%" install >nul 2>&1
)

cd "%APP_DIR%"

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo You can now launch the application.
echo.

timeout /t 3 /nobreak >nul
exit /b 0
