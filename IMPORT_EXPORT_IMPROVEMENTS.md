# Import/Export Improvements

## Problem Fixed
The import functionality was breaking when uploading large backup files (like `amazon_dashboard_ALL_clients_20251006_024115.json` with 8+ clients) because:

1. **Widget Explosion**: Created individual radio buttons for each duplicate client (could be 50+ widgets)
2. **Display Overload**: Tried to display all client names in comma-separated strings
3. **No Progress Feedback**: Large imports had no indication of progress
4. **Memory Issues**: 9MB JSON files loaded with no chunking or feedback

## Changes Made

### Client Import Section (lines 6500-6665)

1. **Simplified Duplicate Handling**: 
   - Changed from per-client radio buttons to a single bulk action choice
   - Two options: "Skip all" or "Overwrite all" duplicates
   - Prevents widget explosion with many clients

2. **Better Display for Large Lists**:
   - Shows counts only for new/duplicate clients
   - Uses expandable sections to view client lists
   - For >20 clients, displays in a scrollable dataframe
   - For ≤20 clients, shows comma-separated list
   - For ≤5 clients, expands automatically

3. **Progress Indication**:
   - Added progress bar during import
   - Shows "Importing X/Y: Client Name" status
   - Clears progress indicators when complete

4. **File Size Warnings on Export**:
   - Displays export file size in KB or MB
   - Warns if export >5MB that import may take longer
   - Suggests exporting fewer clients if experiencing issues

### Data/Session Import Section (lines 9787-9920)

1. **Better Display**:
   - Shows client list in expandable section
   - Uses dataframe for large lists (>20 clients)
   - Auto-expands for ≤5 clients

2. **Progress Indication**:
   - Added progress bar for both clients and sessions
   - Shows current item being imported
   - Clears when complete

## Benefits

✅ **Scalability**: Can now import files with 50+ clients without crashing
✅ **User Feedback**: Clear progress indication during long imports
✅ **Better UX**: Expandable sections keep UI clean
✅ **Performance**: No widget explosion means faster rendering
✅ **Clarity**: File size warnings help users understand what to expect

## Usage

### Export
1. Select clients to export (or use Select All)
2. Click "Export Selected Clients"
3. Review file size information
4. Download the backup file

### Import
1. Upload backup JSON file
2. Review contents (expand to see client lists)
3. Choose import mode (Merge or Replace)
4. For duplicates in Merge mode, choose bulk action
5. Click "Import Clients" and watch progress
6. Wait for completion confirmation

## Technical Details

- **Bulk duplicate action**: Single radio with 2 options instead of N radio buttons
- **Dataframe display**: Uses pandas for efficient large list rendering
- **Progress tracking**: Real-time progress bar with item-by-item status
- **File size calculation**: UTF-8 byte encoding for accurate size
- **Threshold values**: 
  - 20 clients: switches to dataframe display
  - 5 clients: auto-expands lists
  - 5MB: shows large file warning
