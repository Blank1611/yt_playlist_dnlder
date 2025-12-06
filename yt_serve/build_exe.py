"""
Build standalone executable for YouTube Playlist Manager
Requires: pip install pyinstaller
"""
import os
import sys
import subprocess
from pathlib import Path

def build_launcher():
    """Build the launcher executable"""
    
    print("="*60)
    print("Building YouTube Playlist Manager Launcher")
    print("="*60)
    print()
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✓ PyInstaller found")
    except ImportError:
        print("✗ PyInstaller not found")
        print("\nInstalling PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed")
    
    print()
    
    # Create launcher script
    launcher_script = """
import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_python():
    try:
        result = subprocess.run(['python', '--version'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def check_node():
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def main():
    print("YouTube Playlist Manager Launcher")
    print("="*50)
    print()
    
    # Get the directory where the exe is located
    if getattr(sys, 'frozen', False):
        app_dir = Path(sys.executable).parent
    else:
        app_dir = Path(__file__).parent
    
    os.chdir(app_dir)
    
    # Check prerequisites
    print("[1/5] Checking Python...")
    if not check_python():
        print("ERROR: Python not found!")
        print("Please install Python from: https://www.python.org/downloads/")
        input("Press Enter to exit...")
        return
    print("✓ Python found")
    
    print("[2/5] Checking Node.js...")
    if not check_node():
        print("ERROR: Node.js not found!")
        print("Please install Node.js from: https://nodejs.org/")
        input("Press Enter to exit...")
        return
    print("✓ Node.js found")
    
    # Setup backend
    backend_dir = app_dir / "yt_serve" / "backend"
    venv_dir = backend_dir / "venv"
    
    print("[3/5] Setting up backend...")
    if not venv_dir.exists():
        print("  Creating virtual environment...")
        subprocess.run(['python', '-m', 'venv', str(venv_dir)])
        
        print("  Installing dependencies...")
        pip_exe = venv_dir / "Scripts" / "pip.exe"
        requirements = backend_dir / "requirements.txt"
        subprocess.run([str(pip_exe), 'install', '-r', str(requirements)])
        
        # Copy .env.example to .env if not exists
        env_file = backend_dir / ".env"
        env_example = backend_dir / ".env.example"
        if not env_file.exists() and env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            print("  Created .env file - please configure it!")
    print("✓ Backend ready")
    
    # Setup frontend
    frontend_dir = app_dir / "yt_serve" / "frontend"
    node_modules = frontend_dir / "node_modules"
    
    print("[4/5] Setting up frontend...")
    if not node_modules.exists():
        print("  Installing dependencies (this may take 2-3 minutes)...")
        subprocess.run(['npm', 'install'], cwd=str(frontend_dir))
    print("✓ Frontend ready")
    
    # Start servers
    print("[5/5] Starting servers...")
    
    # Start backend
    python_exe = venv_dir / "Scripts" / "python.exe"
    run_py = backend_dir / "run.py"
    backend_process = subprocess.Popen(
        [str(python_exe), str(run_py)],
        cwd=str(backend_dir),
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    
    time.sleep(3)
    
    # Start frontend
    frontend_process = subprocess.Popen(
        ['npm', 'run', 'dev'],
        cwd=str(frontend_dir),
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    
    time.sleep(3)
    
    print()
    print("="*50)
    print("Application started!")
    print("="*50)
    print()
    print("Backend:  http://localhost:8000")
    print("Frontend: http://localhost:5173")
    print()
    print("Opening browser...")
    
    time.sleep(2)
    webbrowser.open('http://localhost:5173')
    
    print()
    print("Application is running!")
    print("Close this window to stop the servers.")
    print()
    
    try:
        backend_process.wait()
    except KeyboardInterrupt:
        print("Shutting down...")
        backend_process.terminate()
        frontend_process.terminate()

if __name__ == '__main__':
    main()
"""
    
    # Write launcher script
    launcher_file = Path("launcher.py")
    launcher_file.write_text(launcher_script)
    print("✓ Created launcher script")
    
    # Build with PyInstaller
    print("\nBuilding executable...")
    print("This may take a few minutes...")
    print()
    
    cmd = [
        'pyinstaller',
        '--onefile',
        '--name=YouTubePlaylistManager',
        '--icon=NONE',
        '--console',
        'launcher.py'
    ]
    
    subprocess.run(cmd)
    
    print()
    print("="*60)
    print("Build Complete!")
    print("="*60)
    print()
    print("Executable location: dist/YouTubePlaylistManager.exe")
    print()
    print("To distribute:")
    print("1. Copy the entire project folder")
    print("2. Include YouTubePlaylistManager.exe in the root")
    print("3. Users just double-click the .exe!")
    print()

if __name__ == '__main__':
    build_launcher()
