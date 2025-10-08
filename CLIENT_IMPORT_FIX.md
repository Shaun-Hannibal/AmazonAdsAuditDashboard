# Client Import Fix - Streamlit Community Cloud

## Issue
When importing a client on Streamlit Community Cloud with Supabase enabled:
- Import appears successful (shows success message)
- App crashes/hangs in "running..." state after ~1 minute
- Client exists in Supabase (confirmed by overwrite prompt) but doesn't appear in "Load Client" dropdown

## Root Cause
1. **Missing cache invalidation** - Supabase uses multi-layer caching:
   - `@st.cache_data` decorators in `supabase_store.py` (10-minute TTL)
   - Session-state cache keys (e.g., `_client_names_cache_{user_id}`, `_config_cache_{user_id}_{client_name}`)
   - App-level cache keys (e.g., `client_config_cache_{client_name}`)
   
2. **No UI refresh** - Unlike the non-Supabase path which auto-loaded the first client and triggered a rerun, the Supabase path just showed a success message without refreshing the UI

3. **Stale cache** - The "Load Client" dropdown kept showing the old cached list that didn't include the newly imported clients

## Fix Applied
Modified the client import logic in `app.py` (lines 6626-6703):

### 1. Comprehensive Cache Clearing (Supabase Mode)
```python
# Clear Supabase session-state cache keys if using Supabase
if use_supabase():
    uid = get_current_user_id()
    if uid:
        # Clear the session-level cache for client names
        cache_key_names = f"_client_names_cache_{uid}"
        st.session_state.pop(cache_key_names, None)
        # Clear individual client config caches
        for client_name in import_data['clients'].keys():
            cache_key_config = f"_config_cache_{uid}_{client_name}"
            st.session_state.pop(cache_key_config, None)
            # Also clear the app-level cache
            app_cache_key = f'client_config_cache_{client_name}'
            st.session_state.pop(app_cache_key, None)
        # Clear the Streamlit @cache_data decorated functions
        try:
            sb_list_client_names.clear()
            sb_fetch_client_config.clear()
        except Exception:
            pass
```

### 2. Auto-Load First Client (All Modes)
```python
# Auto-load first imported client and rerun to refresh UI
if imported_count > 0:
    should_rerun = False
    
    if is_cloud_environment() and not use_supabase():
        # Cloud without Supabase: session-only storage
        # (existing logic)
    else:
        # For all other modes (local, cloud with Supabase), auto-load first client
        try:
            first_imported = list(import_data['clients'].keys())[0]
            st.session_state.selected_client_name = first_imported
            # Load the config to populate session state
            loaded_config = load_client_config(first_imported)
            if loaded_config:
                st.session_state.client_config = loaded_config
                st.session_state.current_page = 'file_uploads'
                should_rerun = True
        except Exception:
            pass
    
    if should_rerun:
        st.balloons()
        st.rerun()
```

## Expected Behavior After Fix
1. ✅ Import client data
2. ✅ All cache layers are invalidated
3. ✅ First imported client is auto-loaded
4. ✅ App navigates to File Uploads page
5. ✅ App reruns to refresh UI
6. ✅ Client appears in "Load Client" dropdown
7. ✅ No crashes or infinite "running..." state

## Testing Recommendations
1. Upload a client backup JSON file
2. Click "Import Clients"
3. Verify the app:
   - Shows success message
   - Auto-loads the first imported client
   - Navigates to File Uploads page
   - Client appears in sidebar dropdown
4. Reload the page and verify client persists (Supabase mode only)
5. Try importing multiple clients and verify all appear in the dropdown

## Related Files
- `app.py` - Client import logic (lines 6542-6717)
- `supabase_store.py` - Supabase data operations with caching
