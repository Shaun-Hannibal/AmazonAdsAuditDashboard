# Advanced Campaign Filtering Feature

## Overview
The Advanced Campaign Filtering system allows you to combine multiple filter rules to quickly select campaigns that match specific criteria, then add them all at once.

## Location
This feature is available in **two places** within the Negatives tab:
1. **Negate Branded Terms/ASINs** section
2. **Negate by Pasted List** section

## How to Use

### Step 1: Add Filter Rules
1. Click the **"➕ Add Filter Rule"** button
2. Multiple rules can be added - each will be combined with AND logic

### Step 2: Configure Each Rule
For each rule, you can:
- Select the condition type:
  - **"contains"** - campaigns that include the text
  - **"doesn't contain"** - campaigns that exclude the text
- Enter the text to filter by (case-insensitive)

### Step 3: View Results
- The system automatically applies all filters
- Shows a success message with the count: ✅ "X campaigns match your filters"
- If no matches, shows a warning: ⚠️ "No campaigns match your filter criteria"

### Step 4: Add Filtered Campaigns
- Click **"Add All Filtered Campaigns"** to select all matching campaigns
- Or manually adjust selections in the multiselect below

### Step 5: Clear Filters (Optional)
- Click **"Clear Filters"** to remove all filter rules
- Remove individual rules with the 🗑️ button

## Example Use Cases

### Example 1: Non-Branded Campaigns
**Goal:** Select all campaigns containing "Non" but not containing "Paused"
- Filter 1: `contains` → `Non`
- Filter 2: `doesn't contain` → `Paused`

### Example 2: Product Type Campaigns
**Goal:** Select campaigns for "apple" products but exclude version "2"
- Filter 1: `contains` → `apple`
- Filter 2: `doesn't contain` → `2`

### Example 3: Region-Specific
**Goal:** Select US campaigns but exclude test campaigns
- Filter 1: `contains` → `US`
- Filter 2: `doesn't contain` → `test`

## Benefits

### Before (Old Way)
- Search for campaigns one at a time
- Manually select each from dropdown
- Tedious for bulk operations

### After (New Way)
- Set multiple filter criteria
- Preview matched count instantly
- Add all matching campaigns with one click
- Significantly faster for bulk operations

## Additional Features

### Quick Selection Buttons
These buttons remain available for common scenarios:
- **"Select All Enabled Non-Branded Campaigns"** - Pre-configured for campaigns containing "Non"
- **"Clear Campaign Selection"** - Clears all selected campaigns

### Manual Selection
The multiselect dropdown remains available for:
- Fine-tuning automated selections
- Manually adding/removing individual campaigns
- Full control when needed
