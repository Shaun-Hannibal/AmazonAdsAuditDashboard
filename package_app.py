#!/usr/bin/env python3
"""
Packaging script for Amazon Dashboard application.
This script creates standalone executables for Windows and Mac.
"""

import os
import sys
import platform
import shutil
import subprocess
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed."""
    try:
        import PyInstaller
        print("✅ PyInstaller already installed")
        return True
    except ImportError:
        print("📦 Installing PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install PyInstaller: {e}")
            return False

def clean_previous_builds():
    """Clean up any previous build artifacts."""
    print("🧹 Cleaning previous builds...")
    
    dirs_to_remove = ['build', 'dist', '__pycache__']
    files_to_remove = ['*.spec']
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")
    
    # Remove spec files
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"   Removed {spec_file}")

def ensure_clean_distribution():
    """Ensure no personal client data will be included in the distribution."""
    print("🔒 Ensuring clean distribution (no personal data)...")
    
    # List client data that will NOT be included in the package
    sensitive_items = []
    
    if os.path.exists('clients') and os.listdir('clients'):
        client_files = [f for f in os.listdir('clients') if f.endswith('.json')]
        if client_files:
            sensitive_items.append(f"clients/ ({len(client_files)} client configs)")
    
    if os.path.exists('client_sessions') and os.listdir('client_sessions'):
        session_dirs = [d for d in os.listdir('client_sessions') if os.path.isdir(os.path.join('client_sessions', d))]
        if session_dirs:
            sensitive_items.append(f"client_sessions/ ({len(session_dirs)} saved sessions)")
    
    if os.path.exists('audit_cache.db'):
        size_mb = os.path.getsize('audit_cache.db') / (1024 * 1024)
        sensitive_items.append(f"audit_cache.db ({size_mb:.1f}MB cache)")
    
    if sensitive_items:
        print("   ✅ The following personal data will NOT be included in the package:")
        for item in sensitive_items:
            print(f"      - {item}")
        print("   ✅ New users will start with a completely clean application")
    else:
        print("   ✅ No personal data found - package will be clean")
    
    return True

def create_spec_file():
    """Create a PyInstaller spec file with proper configuration."""
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'streamlit',
        'plotly',
        'plotly.express',
        'plotly.graph_objects',
        'sklearn',
        'sklearn.linear_model',
        'wordcloud',
        'PIL',
        'PIL.Image',
        'openpyxl',
        'database',
        'insights',
        'asin_helpers',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Amazon_Dashboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/hand_logo.png' if os.path.exists('assets/hand_logo.png') else None,
)
'''
    
    with open('amazon_dashboard.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Created amazon_dashboard.spec file")

def build_application():
    """Build the application using PyInstaller."""
    print("🔨 Building application...")
    
    try:
        # Build using the spec file
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", "amazon_dashboard.spec"]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Application built successfully!")
            return True
        else:
            print("❌ Build failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def create_run_script():
    """Create a simple run script for the executable."""
    system = platform.system()
    
    if system == "Windows":
        script_content = '''@echo off
echo Starting Amazon Dashboard...
Amazon_Dashboard.exe
pause
'''
        script_name = "Run_Amazon_Dashboard.bat"
    else:  # macOS/Linux
        script_content = '''#!/bin/bash
echo "Starting Amazon Dashboard..."
./Amazon_Dashboard
read -p "Press Enter to close..."
'''
        script_name = "Run_Amazon_Dashboard.sh"
    
    script_path = Path("dist") / script_name
    
    if script_path.parent.exists():
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        if system != "Windows":
            os.chmod(script_path, 0o755)  # Make executable
        
        print(f"✅ Created {script_name}")

def get_app_version():
    """Extract version from app.py if available."""
    try:
        with open('app.py', 'r') as f:
            content = f.read()
            # Look for APP_VERSION = "x.x.x"
            import re
            match = re.search(r'APP_VERSION\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
    except:
        pass
    return "1.0.0"

def get_build_info():
    """Get information about the built application."""
    dist_dir = Path("dist")
    if not dist_dir.exists():
        return None
    
    # Find the executable
    system = platform.system()
    if system == "Windows":
        exe_path = dist_dir / "Amazon_Dashboard.exe"
    else:
        exe_path = dist_dir / "Amazon_Dashboard"
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        return {
            'path': exe_path,
            'size_mb': size_mb,
            'system': system,
            'version': get_app_version()
        }
    
    return None

def main():
    """Main packaging function."""
    print("Amazon Dashboard - Application Packaging")
    print("=" * 50)
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Python Version: {platform.python_version()}")
    print()
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found. Please run this script from the Dashboard directory.")
        return False
    
    # Step 1: Install PyInstaller
    if not install_pyinstaller():
        return False
    
    # Step 2: Clean previous builds
    clean_previous_builds()
    
    # Step 3: Ensure clean distribution
    if not ensure_clean_distribution():
        return False
    
    # Step 4: Create spec file
    create_spec_file()
    
    # Step 5: Build application
    if not build_application():
        return False
    
    # Step 6: Create run script
    create_run_script()
    
    # Step 7: Show results
    build_info = get_build_info()
    if build_info:
        print("\n🎉 Packaging completed successfully!")
        print(f"📦 Executable: {build_info['path']}")
        print(f"📏 Size: {build_info['size_mb']:.1f} MB")
        print(f"🏷️  Version: {build_info['version']}")
        print(f"🖥️  Platform: {build_info['system']}")
        print()
        print("📋 Distribution files:")
        dist_files = list(Path("dist").glob("*"))
        for file in dist_files:
            print(f"   {file.name}")
        print()
        print("✅ Your application is ready for distribution!")
        print("   Users can run the executable directly without installing Python.")
        print()
        print("💡 Tips:")
        print("   - Test the executable on a computer without Python installed")
        print("   - The executable will store user data in their Documents/Library folder")
        print("   - First run may be slower as it extracts files")
        
    else:
        print("❌ Build completed but executable not found.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Packaging failed. Check the errors above.")
        sys.exit(1)
    else:
        print("\n✅ Packaging completed successfully!") 