# Cloud Storage Implementation for Streamlit Community Cloud

## Overview
This implementation enables the Amazon Ads Audit Dashboard to work seamlessly on Streamlit Community Cloud by using browser localStorage for data persistence instead of filesystem storage.

## Key Features

### 1. **Automatic Environment Detection**
- `is_cloud_environment()` function detects Streamlit Cloud by checking for `STREAMLIT_SHARING_MODE` environment variable
- Automatically switches between localStorage (cloud) and filesystem (local) storage

### 2. **localStorage JavaScript Bridge**
- Uses `streamlit.components.v1.html()` to execute JavaScript in the browser
- Four core functions:
  - `set_localStorage_value(key, value)` - Store data in browser localStorage
  - `get_localStorage_value(key)` - Retrieve data from browser localStorage
  - `remove_localStorage_value(key)` - Delete data from browser localStorage
  - `list_localStorage_keys(prefix)` - List all keys with a given prefix

### 3. **Cloud-Aware Storage Functions**

#### Client Configuration Storage
- **`save_client_config(client_name, config_data)`**
  - Cloud: Stores in localStorage with key `amazon_dashboard_client_{client_name}`
  - Local: Stores in filesystem at `client_settings/{client_name}.json`
  
- **`load_client_config(client_name)`**
  - Cloud: Retrieves from localStorage
  - Local: Reads from filesystem
  
- **`get_existing_clients()`**
  - Cloud: Retrieves client list from localStorage key `amazon_dashboard_client_list`
  - Local: Scans filesystem directory for `.json` files

#### Session Management
- **`save_audit_session(client_name, session_name, description)`**
  - Cloud: Stores session data and metadata in localStorage
  - Local: Saves to filesystem at `client_sessions/{client_name}/{session_name}.json`
  
- **`load_audit_session(client_name, session_filename)`**
  - Cloud: Retrieves from localStorage
  - Local: Reads from filesystem
  
- **`get_saved_sessions(client_name)`**
  - Cloud: Returns session list from localStorage
  - Local: Scans filesystem directory
  
- **`delete_audit_session(client_name, session_filename)`**
  - Cloud: Removes from localStorage and updates session list
  - Local: Deletes file from filesystem

### 4. **Data Backup & Transfer UI**
Added a new "Data Backup" tab in Client Settings Center with:

#### Export Functionality
- Exports all client configurations and saved sessions to a JSON file
- Includes version info and export timestamp
- Works in both cloud and local modes
- Download button provides timestamped backup file

#### Import Functionality
- Upload previously exported backup files
- Two import modes:
  - **Merge**: Adds to existing data
  - **Replace**: Clears all data first, then imports
- Shows preview of what will be imported (client count, session count)
- Validates backup file format before import

#### User Experience
- Clear indicators showing whether in Cloud Mode or Local Mode
- Helpful tips about data persistence in browser localStorage
- Success/error messages for all operations
- Balloons animation on successful import

## localStorage Key Structure

### Client Data
- **Client list**: `amazon_dashboard_client_list` (JSON array of client names)
- **Client config**: `amazon_dashboard_client_{client_name}` (JSON object)

### Session Data
- **Session list**: `amazon_dashboard_sessions_{client_name}` (JSON array of session metadata)
- **Session data**: `amazon_dashboard_session_data_{client_name}_{filename}` (JSON object)

## Browser localStorage Limits
- Most browsers support 5-10MB per domain
- The implementation handles this gracefully with error messages
- Users can export data to free up space or transfer to another browser

## Testing Recommendations

### Local Testing
1. Run app locally - should use filesystem storage
2. Create clients and sessions
3. Verify files are created in `client_settings/` and `client_sessions/`

### Cloud Testing
1. Deploy to Streamlit Community Cloud
2. Create clients and sessions
3. Open browser DevTools > Application > Local Storage
4. Verify keys are created with `amazon_dashboard_` prefix
5. Test export/import functionality
6. Test data persistence across page refreshes
7. Test in different browsers to verify data isolation

### Cross-Browser Transfer Testing
1. Create data in Browser A
2. Export backup file
3. Open app in Browser B
4. Import backup file
5. Verify all data appears correctly

## Migration Path
For users moving from local to cloud:
1. Run app locally
2. Go to Client Settings > Data Backup tab
3. Click "Export All Data"
4. Download backup file
5. Open app on Streamlit Cloud
6. Go to Client Settings > Data Backup tab
7. Upload backup file and import

## Security Considerations
- localStorage data is stored in the browser and persists across sessions
- Data is isolated per browser/device
- Users should export backups regularly
- No server-side storage means data is only accessible from the browser where it was created
- Clearing browser data will delete all localStorage data

## Future Enhancements
- Add automatic backup reminders
- Implement data compression for larger datasets
- Add selective export/import (specific clients only)
- Add cloud storage options (Google Drive, Dropbox integration)
- Implement data encryption for sensitive information
