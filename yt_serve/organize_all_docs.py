"""
Organize all documentation files in yt_serve into DOCS subdirectory
"""
import shutil
from pathlib import Path

def organize_docs():
    print("="*60)
    print("Organizing yt_serve Documentation")
    print("="*60)
    print()
    
    # Get the directory where this script is located (yt_serve/)
    yt_serve = Path(__file__).parent.resolve()
    docs_dir = yt_serve / "DOCS"
    
    print(f"Working directory: {yt_serve}")
    print()
    
    # Create DOCS directory if it doesn't exist
    docs_dir.mkdir(exist_ok=True)
    print(f"✓ Created/verified DOCS directory")
    
    # List of all markdown files to move (excluding README.md which stays in root)
    doc_files = [
        "BACKEND_CONFIG.md",
        "BROWSER_LIMITATIONS.md",
        "COMPLETE.md",
        "COMPLETE_INSTALLER_SOLUTION.md",
        "DEVELOPER_GUIDE.md",
        "DOCS_ORGANIZATION.md",
        "END_USER_GUIDE.md",
        "END_USER_SOLUTIONS.md",
        "EXCLUSIONS_FEATURE.md",
        "FIRST_RUN_SETUP.md",
        "FRONTEND_COMPLETE.md",
        "GETTING_STARTED.md",
        "IMPLEMENTATION_STATUS.md",
        "INDEPENDENCE_COMPLETE.md",
        "KNOWN_ISSUES.md",
        "LATEST_IMPROVEMENTS.md",
        "LOGGING_ARCHITECTURE.md",
        "MAINTENANCE_NOTES.md",
        "MIGRATION_GUIDE.md",
        "MIGRATION_SUCCESS.md",
        "NODE_MODULES_EXPLAINED.md",
        "QUICKSTART.md",
        "SETUP_GUIDE.md",
        "TESTING_GUIDE.md",
        "TROUBLESHOOTING.md",
        "UI_IMPROVEMENTS.md",
    ]
    
    # Move files
    moved = 0
    skipped = 0
    
    print("\nMoving documentation files...")
    for file in doc_files:
        src = yt_serve / file
        dest = docs_dir / file
        
        if src.exists():
            if dest.exists():
                print(f"  ⚠ {file} already exists in DOCS/")
                skipped += 1
            else:
                shutil.move(str(src), str(dest))
                print(f"  ✓ {file} -> DOCS/")
                moved += 1
        else:
            print(f"  - {file} not found (skipping)")
    
    # Create DOCS README
    print("\nCreating DOCS/README.md...")
    docs_readme = docs_dir / "README.md"
    
    readme_content = """# yt_serve Documentation

Complete documentation for the YouTube Playlist Manager web application.

## Quick Links

### Getting Started
- **[QUICKSTART.md](QUICKSTART.md)** - Quick setup guide
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Detailed getting started guide
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete setup instructions
- **[FIRST_RUN_SETUP.md](FIRST_RUN_SETUP.md)** - First-run setup wizard guide

### User Guides
- **[END_USER_GUIDE.md](END_USER_GUIDE.md)** - Complete user guide
- **[END_USER_SOLUTIONS.md](END_USER_SOLUTIONS.md)** - Common solutions
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Troubleshooting guide

### Features
- **[EXCLUSIONS_FEATURE.md](EXCLUSIONS_FEATURE.md)** - Video exclusions feature
- **[UI_IMPROVEMENTS.md](UI_IMPROVEMENTS.md)** - UI features and improvements
- **[FRONTEND_COMPLETE.md](FRONTEND_COMPLETE.md)** - Frontend features

### Technical Documentation
- **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** - Developer guide
- **[BACKEND_CONFIG.md](BACKEND_CONFIG.md)** - Backend configuration system
- **[LOGGING_ARCHITECTURE.md](LOGGING_ARCHITECTURE.md)** - Logging system
- **[INDEPENDENCE_COMPLETE.md](INDEPENDENCE_COMPLETE.md)** - Project independence
- **[MAINTENANCE_NOTES.md](MAINTENANCE_NOTES.md)** - Maintenance guidelines

### Installation & Deployment
- **[COMPLETE_INSTALLER_SOLUTION.md](COMPLETE_INSTALLER_SOLUTION.md)** - Installer guide
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Migration from Tkinter version
- **[MIGRATION_SUCCESS.md](MIGRATION_SUCCESS.md)** - Migration success notes

### Testing
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Testing guide

### Reference
- **[BROWSER_LIMITATIONS.md](BROWSER_LIMITATIONS.md)** - Browser limitations
- **[NODE_MODULES_EXPLAINED.md](NODE_MODULES_EXPLAINED.md)** - Node modules info
- **[KNOWN_ISSUES.md](KNOWN_ISSUES.md)** - Known issues
- **[IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)** - Implementation status
- **[LATEST_IMPROVEMENTS.md](LATEST_IMPROVEMENTS.md)** - Latest improvements
- **[COMPLETE.md](COMPLETE.md)** - Completion notes

### Organization
- **[DOCS_ORGANIZATION.md](DOCS_ORGANIZATION.md)** - Documentation organization

## Documentation Categories

### 📚 For End Users
Start here if you're using the app:
1. [QUICKSTART.md](QUICKSTART.md) - Get up and running quickly
2. [END_USER_GUIDE.md](END_USER_GUIDE.md) - Learn all features
3. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Fix common issues

### 🔧 For Developers
Start here if you're developing or customizing:
1. [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Development setup
2. [BACKEND_CONFIG.md](BACKEND_CONFIG.md) - Backend architecture
3. [MAINTENANCE_NOTES.md](MAINTENANCE_NOTES.md) - Maintenance tips

### 🚀 For Deployment
Start here if you're deploying or distributing:
1. [SETUP_GUIDE.md](SETUP_GUIDE.md) - Complete setup
2. [COMPLETE_INSTALLER_SOLUTION.md](COMPLETE_INSTALLER_SOLUTION.md) - Create installer
3. [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Migrate from Tkinter

## Project Structure

```
yt_serve/
├── README.md                    # Main project overview
├── DOCS/                        # All documentation (you are here)
│   ├── README.md               # This file
│   ├── QUICKSTART.md           # Quick start
│   └── ... (all other docs)
├── backend/                     # Python FastAPI backend
├── frontend/                    # React TypeScript frontend
├── LAUNCH_APP.bat              # One-click launcher
└── ... (other files)
```

## Need Help?

1. **Quick answer?** Check [QUICKSTART.md](QUICKSTART.md)
2. **Setup issue?** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. **Feature question?** Read [END_USER_GUIDE.md](END_USER_GUIDE.md)
4. **Development?** Start with [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)

## Contributing

If you're adding new documentation:
1. Place it in this DOCS/ directory
2. Update this README.md with a link
3. Use clear, descriptive filenames
4. Follow existing documentation style
"""
    
    with open(docs_readme, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("  ✓ Created DOCS/README.md")
    
    print()
    print("="*60)
    print("Documentation Organization Complete!")
    print("="*60)
    print()
    print(f"Moved: {moved} files")
    print(f"Skipped: {skipped} files (already in DOCS/)")
    print()
    print("Structure:")
    print("  yt_serve/")
    print("    ├── README.md              (main project overview)")
    print("    ├── DOCS/                  (all documentation)")
    print("    │   ├── README.md         (documentation index)")
    print(f"    │   └── ... ({moved} doc files)")
    print("    ├── backend/")
    print("    ├── frontend/")
    print("    └── ... (other files)")
    print()

if __name__ == '__main__':
    organize_docs()
