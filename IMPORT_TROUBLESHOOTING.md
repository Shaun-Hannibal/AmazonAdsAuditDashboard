# Import/Export Troubleshooting Guide

## Common Issues & Solutions

### Issue: Import Breaks with Large Files

**Symptoms:**
- App crashes or hangs when importing backup files
- "Widget limit exceeded" error
- Browser becomes unresponsive

**Solution:**
✅ **FIXED** - The new version uses bulk duplicate handling instead of creating individual widgets for each client.

---

### Issue: Can't See All Clients in Import Preview

**Symptoms:**
- Client list is cut off or unreadable
- Too many names in one line

**Solution:**
✅ **FIXED** - New version uses expandable sections with scrollable dataframes for large lists.

---

### Issue: Import Takes Too Long with No Feedback

**Symptoms:**
- Import appears to hang
- No way to tell if it's working
- Not sure if browser crashed

**Solution:**
✅ **FIXED** - Added progress bar and status text showing which client is being imported.

---

## Best Practices

### For Cloud Mode (Streamlit Community Cloud)

Since you removed Supabase and are using localStorage:

1. **Export Regularly**: Browser data can be cleared
2. **Keep Backups Local**: Download exports to your computer
3. **Test Imports**: After importing, verify a few clients loaded correctly
4. **Split Large Exports**: If you have 20+ clients, consider exporting in smaller batches

### For Local Development

1. **Use Filesystem**: Local mode stores directly to `clients/` directory
2. **Backups Are Optional**: Files persist automatically
3. **Large Imports OK**: Filesystem handles large files better than browser storage

---

## Import Modes Explained

### Merge Mode
- Keeps existing clients that aren't in the backup
- For duplicates, you choose: Skip all or Overwrite all
- Good for: Adding new clients from coworker's backup

### Replace Mode
- **DELETES ALL** existing clients first
- Then imports everything from backup
- Good for: Starting fresh or restoring complete backup

---

## File Size Guidelines

| File Size | Status | Import Speed | Recommendation |
|-----------|--------|--------------|----------------|
| < 1 MB | ✅ Fast | < 5 seconds | No issues |
| 1-5 MB | ✅ OK | 5-15 seconds | Watch progress bar |
| 5-10 MB | ⚠️ Large | 15-30 seconds | Consider splitting |
| > 10 MB | 🚨 Very Large | 30+ seconds | Split into batches |

---

## Duplicate Handling Strategy

The new bulk approach asks ONE question for ALL duplicates:

**"Skip all" (Keep existing)**
- Your current data remains unchanged
- Only new clients from backup are added
- Use when: You want to add new clients without touching existing ones

**"Overwrite all" (Replace with backup)**
- All duplicates replaced with backup versions
- Useful for restoring from a known-good backup
- Use when: Backup has more recent/correct data

---

## Testing Your Import

After importing, verify:

1. ✅ Client count matches expectations
2. ✅ Open 2-3 clients to check data loaded
3. ✅ Check Client Settings for branded ASINs
4. ✅ Try uploading bulk file to verify functionality

---

## Cloud Mode Caveats

Without Supabase, clients are stored in **browser localStorage**:

- ⚠️ Cleared if you clear browser data
- ⚠️ Not shared across devices
- ⚠️ Not shared across browsers
- ⚠️ Limited storage space (~10MB typical)

**Workaround**: Export regularly and store JSON files somewhere safe (Google Drive, Dropbox, etc.)

---

## Emergency Recovery

If something goes wrong during import:

1. **Don't panic** - Your original files should still be backed up
2. **Refresh the page** - Clears partial import state
3. **Re-import with Replace mode** - Ensures clean slate
4. **Check browser console** - Look for error messages (F12 > Console)

If data appears corrupted:
1. Go to Client Selection
2. Choose "Import Client Data"
3. Upload your most recent good backup
4. Select "Replace" mode
5. Import and refresh

---

## Performance Tips

### For Faster Imports
1. Use local development mode when possible
2. Import during off-peak hours
3. Close unnecessary browser tabs
4. Use modern browsers (Chrome, Edge, Firefox)

### For Reliable Storage
1. **Best**: Use localhost (filesystem storage)
2. **Good**: Configure Supabase (persistent cloud DB)
3. **OK**: Browser localStorage + regular exports
4. **Avoid**: Browser localStorage without backups
