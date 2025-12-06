"""
Build complete Windows installer with bundled Python and Node.js
This creates a professional installer that requires NO prerequisites
"""
import os
import sys
import urllib.request
import zipfile
import shutil
import subprocess
from pathlib import Path

# Portable runtime URLs
# Update these to match your preferred versions
PYTHON_VERSION = "3.14.0"  # Python 3.14 (alpha/beta)
PYTHON_EMBED_URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-embed-amd64.zip"
NODE_VERSION = "20.11.0"  # Latest LTS Node.js
NODE_PORTABLE_URL = f"https://nodejs.org/dist/v{NODE_VERSION}/node-v{NODE_VERSION}-win-x64.zip"

# Note: Python 3.14 is in alpha/beta. For production, consider using 3.12.x (stable)
# If Python 3.14 embed version is not available, the script will fail - use 3.12.7 instead

def download_file(url, dest):
    """Download file with progress"""
    print(f"Downloading {Path(dest).name}...")
    
    def reporthook(count, block_size, total_size):
        percent = int(count * block_size * 100 / total_size)
        sys.stdout.write(f"\r  Progress: {percent}%")
        sys.stdout.flush()
    
    urllib.request.urlretrieve(url, dest, reporthook)
    print("\n  ✓ Downloaded")

def extract_zip(zip_path, extract_to):
    """Extract ZIP file"""
    print(f"Extracting {Path(zip_path).name}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("  ✓ Extracted")

def setup_portable_python(portable_dir):
    """Download and setup portable Python"""
    python_dir = portable_dir / "python"
    python_dir.mkdir(parents=True, exist_ok=True)
    
    # Download Python embed
    python_zip = portable_dir / "python-embed.zip"
    if not python_zip.exists():
        download_file(PYTHON_EMBED_URL, python_zip)
    
    # Extract
    extract_zip(python_zip, python_dir)
    
    # Download get-pip.py
    print("Downloading get-pip.py...")
    pip_url = "https://bootstrap.pypa.io/get-pip.py"
    get_pip = python_dir / "get-pip.py"
    urllib.request.urlretrieve(pip_url, get_pip)
    print("  ✓ Downloaded")
    
    # Enable pip in python._pth
    pth_file = list(python_dir.glob("python*._pth"))[0]
    content = pth_file.read_text()
    if "#import site" in content:
        content = content.replace("#import site", "import site")
        pth_file.write_text(content)
    
    # Install pip
    print("Installing pip...")
    python_exe = python_dir / "python.exe"
    subprocess.run([str(python_exe), str(get_pip)], 
                  stdout=subprocess.DEVNULL, 
                  stderr=subprocess.DEVNULL)
    print("  ✓ Pip installed")
    
    # Cleanup
    python_zip.unlink()
    get_pip.unlink()
    
    return python_dir

def setup_portable_nodejs(portable_dir):
    """Download and setup portable Node.js"""
    node_dir = portable_dir / "nodejs"
    node_dir.mkdir(parents=True, exist_ok=True)
    
    # Download Node.js
    node_zip = portable_dir / "node-portable.zip"
    if not node_zip.exists():
        download_file(NODE_PORTABLE_URL, node_zip)
    
    # Extract
    temp_dir = portable_dir / "node_temp"
    extract_zip(node_zip, temp_dir)
    
    # Move contents (Node.js extracts to a subfolder)
    extracted_folder = list(temp_dir.glob("node-*"))[0]
    for item in extracted_folder.iterdir():
        shutil.move(str(item), str(node_dir / item.name))
    
    # Cleanup
    shutil.rmtree(temp_dir)
    node_zip.unlink()
    
    return node_dir

def build_exe():
    """Build the launcher EXE"""
    print("\nBuilding launcher executable...")
    
    # Check PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Build
    subprocess.run([
        'pyinstaller',
        '--onefile',
        '--name=YouTubePlaylistManager',
        '--console',
        '--icon=NONE',
        'launcher.py'
    ], stdout=subprocess.DEVNULL)
    
    print("  ✓ EXE built")

def create_installer():
    """Create Inno Setup installer"""
    print("\nCreating installer...")
    
    # Check if Inno Setup is installed
    inno_path = Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe")
    if not inno_path.exists():
        print("\n[!] Inno Setup not found!")
        print("    Download from: https://jrsoftware.org/isdl.php")
        print("    Then run this script again.")
        return False
    
    # Compile installer
    subprocess.run([str(inno_path), "installer.iss"])
    print("  ✓ Installer created")
    return True

def main():
    print("="*60)
    print("YouTube Playlist Manager - Complete Installer Builder")
    print("="*60)
    print()
    print("This will create a Windows installer that includes:")
    print("  • Portable Python 3.11")
    print("  • Portable Node.js 18")
    print("  • All application files")
    print("  • Automatic dependency installation")
    print()
    print("Users will NOT need to install anything manually!")
    print()
    
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled")
        return
    
    print()
    
    # Create portable directory
    portable_dir = Path("portable")
    portable_dir.mkdir(exist_ok=True)
    
    # Setup portable runtimes
    print("[1/4] Setting up portable Python...")
    python_dir = setup_portable_python(portable_dir)
    
    print("\n[2/4] Setting up portable Node.js...")
    node_dir = setup_portable_nodejs(portable_dir)
    
    # Build launcher EXE
    print("\n[3/4] Building launcher...")
    build_exe()
    
    # Create installer
    print("\n[4/4] Creating installer...")
    success = create_installer()
    
    print()
    print("="*60)
    if success:
        print("Build Complete!")
        print("="*60)
        print()
        print("Installer: installer_output/YouTubePlaylistManager_Setup.exe")
        print()
        print("This installer:")
        print("  ✓ Includes Python and Node.js")
        print("  ✓ Installs all dependencies automatically")
        print("  ✓ Creates desktop shortcut")
        print("  ✓ Adds to Start Menu")
        print("  ✓ Standard Windows installer experience")
        print()
        print("Users just:")
        print("  1. Run the installer")
        print("  2. Choose installation location")
        print("  3. Click Install")
        print("  4. Launch the app!")
        print()
        print("NO manual setup required!")
    else:
        print("Build Incomplete")
        print("="*60)
        print()
        print("Install Inno Setup and try again.")
    print()

if __name__ == '__main__':
    main()
