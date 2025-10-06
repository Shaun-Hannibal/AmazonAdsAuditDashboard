#!/usr/bin/env python3
"""
Launcher script for the Amazon Advertising Dashboard.
This wrapper allows PyInstaller to bundle the Streamlit app into a single executable
that users can double-click without installing Python.
"""
import os
import sys

try:
    # When frozen by PyInstaller, resources are extracted to sys._MEIPASS.
    if getattr(sys, "frozen", False):
        MEIPASS = getattr(sys, "_MEIPASS", None)
        BASE_PATH = MEIPASS if MEIPASS else os.path.dirname(sys.executable)
    else:
        BASE_PATH = os.path.dirname(__file__)
except AttributeError:
    BASE_PATH = os.path.dirname(__file__)

# Ensure any relative file reads/writes occur where bundled data lives
os.chdir(BASE_PATH)

# Ensure Streamlit runs on a predictable port and without dev server quirks
# Allow Streamlit to auto-launch browser
os.environ.setdefault("STREAMLIT_SERVER_HEADLESS", "false")
# On macOS, ensure the default 'open' command is used
os.environ.setdefault("BROWSER", "open")
# Disable file watcher in frozen/packaged mode to prevent infinite reruns
os.environ.setdefault("STREAMLIT_SERVER_FILE_WATCHER_TYPE", "none")
# Disable anonymous usage stats collection
os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")

import streamlit.web.cli as st_cli  # pylint: disable=import-error

# Determine path to app.py irrespective of whether we're running frozen or not
app_candidate_paths = [
    os.path.join(BASE_PATH, "app.py"),
    os.path.join(BASE_PATH, "_internal", "app.py"),
]
for p in app_candidate_paths:
    if os.path.exists(p):
        APP_PATH = p
        break
else:
    # Fallback to streamlit default search (will error but give useful message)
    APP_PATH = "app.py"

# Replace argv so Streamlit runs with explicit config flags using absolute path
sys.argv = [
    "streamlit",
    "run",
    os.path.abspath(APP_PATH),
    "--global.developmentMode=false",
]

if __name__ == "__main__":
    # Delegate to Streamlit's CLI entry point
    sys.exit(st_cli.main())
