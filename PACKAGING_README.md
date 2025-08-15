# Amazon Dashboard - Packaging Instructions

This document explains how to package your Amazon Dashboard application into standalone executables for Windows and Mac users.

## Quick Start

1. **Run the packaging script:**
   ```bash
   python package_app.py
   ```

2. **Find your executable in the `dist/` folder**

3. **Test the executable on a clean system**

## What the Packaging Script Does

✅ **Fixes Applied:**
- **Data Storage**: User data now goes to proper OS locations (not application directory)
  - **Windows**: `%APPDATA%\AmazonDashboard\`
  - **Mac**: `~/Library/Application Support/AmazonDashboard/`
  - **Fallback**: `~/Documents/AmazonDashboard/` (for work computers with restrictions)

✅ **Memory Protection**: Added file size warnings for large uploads

✅ **Clean Build**: Removes large template files and old build artifacts

✅ **Privacy Protection**: Your personal client data is NOT included in the packaged application - new users start with a completely clean program

## File Locations for End Users

When users run your packaged application, their data will be stored in:

### Windows:
```
C:\Users\[username]\AppData\Roaming\AmazonDashboard\
├── clients/           (Client configurations)
├── client_sessions/   (Saved analysis sessions)
└── audit_cache.db     (Performance cache database)
```

### Mac:
```
/Users/[username]/Library/Application Support/AmazonDashboard/
├── clients/           (Client configurations)
├── client_sessions/   (Saved analysis sessions)
└── audit_cache.db     (Performance cache database)
```

### Work Computers (Fallback):
```
/Users/[username]/Documents/AmazonDashboard/  (Mac)
C:\Users\[username]\Documents\AmazonDashboard\  (Windows)
```

## Distribution

The packaging script creates:
- `Amazon_Dashboard.exe` (Windows) or `Amazon_Dashboard` (Mac)
- `Run_Amazon_Dashboard.bat` (Windows) or `Run_Amazon_Dashboard.sh` (Mac)

**Distribution size**: Expect ~300-500MB (includes Python, all dependencies, and assets)

## What Gets Included vs Excluded

### ✅ **Included in Package:**
- Application code (`app.py`, `database.py`, `insights.py`, etc.)
- Assets folder (logos, icons)
- Python runtime and all dependencies
- Empty directory structure for user data

### ❌ **NOT Included (Your Private Data):**
- `clients/` - Your 8 client JSON configurations
- `client_sessions/` - Your saved analysis sessions
- `audit_cache.db` - Your performance cache database
- Any uploaded reports or analysis data

**Result**: New users get a completely fresh application with no access to your client data.

## Version Management & Updates

### 📝 **Before Packaging:**
- **Edit freely**: Make any changes to `app.py`, `database.py`, `insights.py`
- **Test locally**: Use `streamlit run app.py` to verify changes
- **Update version**: Change `APP_VERSION = "1.0.0"` in `app.py` for new releases

### 🔄 **Creating Updates:**
1. **Make your code changes**
2. **Update the version number** in `app.py`:
   ```python
   APP_VERSION = "1.1.0"  # Bug fix
   APP_VERSION = "2.0.0"  # Major feature
   ```
3. **Test thoroughly**
4. **Re-run packaging**: `python package_app.py`
5. **Distribute new executable**

### ✅ **User Data Preservation:**
When users install updates, their data is **automatically preserved**:
- ✅ Client configurations remain intact
- ✅ Saved analysis sessions are preserved  
- ✅ Database cache continues working
- ✅ No manual migration needed

The new executable will automatically find and use their existing data in the user directory.

### 📋 **Version Tracking:**
The packaging script automatically:
- Extracts version from your `APP_VERSION` in `app.py`
- Displays version during packaging
- Helps you track what version you're distributing

### 🔧 **Development Workflow:**
```bash
# 1. Make changes
vim app.py

# 2. Test locally  
streamlit run app.py

# 3. Update version
# APP_VERSION = "1.1.0" 

# 4. Package
python package_app.py

# 5. Distribute
# Send new executable to users
```

## Testing Checklist

Before distributing, test on:

### Windows:
- [ ] Windows 10/11 without Python installed
- [ ] Work computer with restricted permissions
- [ ] 8GB RAM system (test with large files)
- [ ] Different user accounts

### Mac:
- [ ] macOS 10.15+ without Python installed
- [ ] Work computer with restricted permissions
- [ ] 8GB RAM system (test with large files)
- [ ] Different user accounts

## Common Issues & Solutions

### "Permission Denied" Errors
- The app now automatically handles this by trying multiple data locations
- Users on restricted work computers should see data in their Documents folder

### "Out of Memory" Errors
- The app now warns users about large files (>50MB)
- Consider recommending 16GB+ RAM for users with very large datasets

### Slow Startup
- First run is slower as PyInstaller extracts files
- Subsequent runs are much faster

### Antivirus False Positives
- Some antivirus software flags PyInstaller executables
- This is normal and can be resolved by:
  - Adding exclusions for the executable
  - Code signing (for commercial distribution)

## File Size Optimization

Current optimizations applied:
- Removed large template files
- UPX compression enabled
- Excluded unnecessary modules

If you need smaller executables:
- Consider using `--exclude-module` for unused packages
- Use `--onedir` instead of `--onefile` for faster startup

## Code Signing (Optional)

For commercial distribution, consider code signing:

### Windows:
```bash
signtool sign /f certificate.p12 /p password Amazon_Dashboard.exe
```

### Mac:
```bash
codesign --force --verify --verbose --sign "Developer ID" Amazon_Dashboard
```

## Troubleshooting

### Build Fails
1. Check that all dependencies are installed: `pip install -r requirements.txt`
2. Run `python test_data_directory.py` to verify data directory setup
3. Check the error output for missing modules

### Executable Won't Start
1. Test with `console=True` in the spec file for debugging
2. Check if antivirus is blocking the executable
3. Verify all data directories can be created

### Application Crashes
1. Test with smaller files first
2. Check available RAM
3. Look for permission issues in the data directory

## Support

For packaging issues:
1. Run `python test_data_directory.py` to test data directory setup
2. Check the build output for errors
3. Test on a clean system without Python installed 