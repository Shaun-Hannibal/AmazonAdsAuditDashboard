# Distribution Guide - Amazon Advertising Dashboard

## Overview
The `dist/` folder contains the standalone executable version of the Amazon Advertising Dashboard that runs **exactly** like `streamlit run app.py` on localhost.

## What's Included in the Executable

### Core Application Files
- ✅ **app.py** - Main Streamlit application
- ✅ **database.py** - Database management module
- ✅ **supabase_store.py** - Supabase integration module
- ✅ **run_dashboard.py** - Launcher script

### Assets & Configuration
- ✅ **assets/** - Logo and image files
- ✅ **.streamlit/config.toml** - Streamlit configuration (dark theme, settings)

### Dependencies (All Bundled)
- ✅ Streamlit 1.28.0
- ✅ Pandas, NumPy, Plotly
- ✅ OpenPyXL (Excel support)
- ✅ WordCloud, Matplotlib
- ✅ Scikit-learn (linear regression)
- ✅ Supabase client libraries
- ✅ PIL/Pillow (image processing)

## Files in dist/
```
dist/
├── Amazon_Dashboard          # Main executable (~126 MB)
└── Run_Amazon_Dashboard.sh   # Convenience launcher script
```

## How to Run

### Option 1: Double-click the Executable
Simply double-click `Amazon_Dashboard` to launch the application.

### Option 2: Use the Shell Script
```bash
cd dist/
./Run_Amazon_Dashboard.sh
```

### Option 3: Direct Execution
```bash
cd dist/
./Amazon_Dashboard
```

## Expected Behavior

When launched, the executable will:
1. **Extract bundled files** to a temporary location (first run is slower)
2. **Start Streamlit server** on localhost (default port 8501)
3. **Auto-open browser** to the dashboard
4. **Disable file watcher** (no auto-reloads like dev mode)
5. **Create data directories** in user's home folder for:
   - Client configurations
   - Session data
   - Settings

## User Data Storage

The executable stores user data in platform-appropriate locations:

### macOS
```
~/Library/Application Support/Amazon_Dashboard/
├── clients/          # Client configuration files
├── client_sessions/  # Saved analysis sessions
└── client_settings/  # User preferences
```

### Windows
```
%APPDATA%\Amazon_Dashboard\
├── clients\
├── client_sessions\
└── client_settings\
```

## Differences from Localhost Development

### Same Behavior
- ✅ All features work identically
- ✅ Same UI, styling, and theme
- ✅ Same data processing logic
- ✅ Supabase authentication (if configured)
- ✅ Local storage fallback

### Key Differences
- ⚠️ **No auto-reload** - File watcher is disabled (intentional for stability)
- ⚠️ **First run slower** - Extracting bundled files takes 10-20 seconds
- ⚠️ **Isolated data** - User data stored in system folders, not project directory
- ⚠️ **No Python required** - Users don't need Python installed

## Clean Distribution Policy

Per user preference (MEMORY[eb633c47-2a9a-4877-bcd0-779f852c214c]), the packaged distribution:
- ❌ **Never includes personal data**
- ❌ **No client configs** from developer's machine
- ❌ **No cached sessions**
- ❌ **No audit cache database**

End users always start with a clean slate.

## Testing the Executable

### Recommended Test Steps
1. Run the executable on your development machine
2. Verify all features work (import, export, analysis, optimization)
3. Test on a clean machine without Python installed
4. Verify browser auto-opens to localhost:8501
5. Test client import/export functionality
6. Verify Supabase authentication (if enabled)

### Known Issues to Watch For
- **Port conflicts** - If 8501 is in use, Streamlit will try 8502, 8503, etc.
- **Firewall prompts** - First run may trigger security dialogs
- **macOS Gatekeeper** - May require "Allow apps from App Store and identified developers"

## Rebuilding the Distribution

To rebuild with latest changes:

```bash
# Navigate to project root
cd /Users/shaun/Documents/Python\ Projects/Dashboard/

# Run packaging script
python3 package_app.py
```

This will:
1. Clean previous builds
2. Verify no personal data is included
3. Create updated spec file
4. Build new executable with PyInstaller
5. Generate launcher script

## Streamlit Configuration

The executable uses the same configuration as localhost:

**Theme Settings** (from `.streamlit/config.toml`):
- Base: Dark
- Primary Color: #4F8BF9
- Background: #1E1E1E
- Secondary Background: #262626
- Text: #FAFAFA

**Server Settings**:
- Development Mode: Disabled
- File Watcher: None (no auto-reloads)
- CORS: Disabled
- Usage Stats: Disabled

## Version Information

- **App Version**: 1.0.0 (from `APP_VERSION` in app.py)
- **Platform**: Built on macOS (Darwin)
- **Python**: 3.9.6
- **PyInstaller**: Latest compatible version

## Troubleshooting

### Executable won't launch
- Check system logs for errors
- Verify you have execute permissions: `chmod +x Amazon_Dashboard`
- Try running from terminal to see error messages

### Browser doesn't auto-open
- Manually navigate to http://localhost:8501
- Check if another app is using port 8501

### Missing features or errors
- Verify all Python dependencies are in `requirements.txt`
- Check `hiddenimports` in `package_app.py` spec file
- Rebuild with `python3 package_app.py`

### Performance issues
- First run is always slower (extracting files)
- Subsequent runs should be fast
- Check available disk space (needs ~200MB temp space)

## Distribution Checklist

Before distributing to users:

- [ ] Test executable on development machine
- [ ] Test on clean machine without Python
- [ ] Verify all features work (import, export, analysis)
- [ ] Confirm no personal data is included
- [ ] Test browser auto-launch
- [ ] Verify data directories are created correctly
- [ ] Test with/without Supabase configuration
- [ ] Document any system requirements
- [ ] Include this README with distribution

## Support

For issues with the executable:
1. Check this guide's troubleshooting section
2. Run from terminal to capture error messages
3. Verify system requirements are met
4. Try rebuilding with latest `package_app.py`

## Technical Details

### PyInstaller Configuration
- **Entry Point**: `run_dashboard.py`
- **Bundle Mode**: Single file (`--onefile`)
- **Console**: Disabled (no terminal window)
- **Icon**: `assets/hand_logo.png`
- **UPX**: Enabled (compression)

### Metadata Bundles
Included for proper module initialization:
- streamlit, pandas, plotly, openpyxl
- typing_extensions, narwhals

### Data Files Included
All necessary runtime files are bundled:
- Python scripts (app.py, database.py, supabase_store.py)
- Streamlit static files and templates
- Plotly chart templates
- Configuration files (.streamlit/config.toml)
- Assets (logos, images)

### Hidden Imports
All dynamic imports are explicitly declared to prevent runtime errors:
- Streamlit runtime and components
- Pandas/NumPy internal modules
- Plotly graph objects
- Matplotlib backends
- OpenPyXL utilities
- Supabase client libraries
- Sklearn models

---

**Last Updated**: 2025-10-10
**Built By**: package_app.py (automated packaging script)
