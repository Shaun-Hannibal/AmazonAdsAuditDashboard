# Supabase Import/Export Fix

## Issue
The app was crashing during import/export operations due to lingering Supabase code attempting to access Supabase even though the user stopped using it.

## Root Cause
1. `use_supabase()` returns `True` if:
   - Running in cloud environment (Streamlit Cloud)
   - `SUPABASE_URL` and `SUPABASE_ANON_KEY` exist in secrets

2. When Supabase is "enabled" but user is not logged in:
   - `load_client_config()` returns `None` → export fails with no data
   - `save_client_config()` returns early with error → import fails silently

3. This caused:
   - Export producing empty client data
   - Import failing to save any clients
   - Silent failures with no clear error messages

## Solutions Implemented

### 1. Better Error Detection in Export
- Track failed client loads during export
- Show specific error if Supabase auth is the issue
- Prevent exporting empty files
- Guide user to disable Supabase if not using it

### 2. Better Error Handling in Import
- Check Supabase auth status before import loop
- Wrap each client save in try-except
- Show specific errors per client
- Continue importing other clients if one fails

### 3. User-Friendly Error Messages
- Clear indication when Supabase auth is blocking operations
- Actionable guidance: "disable Supabase in the sidebar"
- Prevent silent failures

## How to Permanently Fix

Choose one option:

### Option 1: Disable via Streamlit Secrets (Recommended)
Add to your Streamlit Cloud app secrets:
```toml
FORCE_NO_SUPABASE = true
```

### Option 2: Remove Supabase Secrets
Delete these from your secrets:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`

### Option 3: Use UI Toggle (Temporary)
Check the **"Disable Supabase (session-only)"** checkbox in the sidebar.

## Changes Made
- Enhanced `load_client_config()` error handling in export
- Added auth check before import loop
- Wrapped individual client imports in try-except
- Added helpful error messages pointing to Supabase as the cause
- Prevent export of empty files

## Testing
Test import/export with the Three_Dog_Bakery_export.json file to verify the fixes work correctly.
