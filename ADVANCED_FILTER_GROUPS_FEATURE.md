# Advanced Filter Groups with AND/OR Logic

## Overview
The Negative Keywords tab now supports **advanced filter groups with AND/OR logic** for campaign filtering. This allows complex, multi-condition filtering to quickly select the exact campaigns you need.

## Location
- **Negatives** tab → **Negate Branded Terms** section → Advanced Campaign Filtering
- **Negatives** tab → **Negate by Pasted List** section → Advanced Campaign Filtering

## Feature Components

### 1. Filter Groups
- Create multiple **independent filter groups**
- Each group can contain **multiple filter rules**
- Groups are visually separated for clarity

### 2. Filter Rules
Each rule consists of:
- **Condition**: `contains` or `doesn't contain`
- **Text**: The search string to match against campaign names (case-insensitive)

### 3. Logic Operators

#### Within Group Logic (Rules)
- **AND**: Campaign must match **ALL rules** in the group
- **OR**: Campaign must match **AT LEAST ONE rule** in the group

#### Between Groups Logic
- **AND**: Campaign must match **ALL groups**
- **OR**: Campaign must match **AT LEAST ONE group**

## User Interface

### Control Panel
```
[➕ Add Filter Group] [Between Groups: AND/OR ▼] [Clear All]
```

### Group Structure
```
Group 1
├─ [Rules Logic: AND ▼] [➕ Add Rule] [🗑️ Group]
├─ Rule 1: [contains ▼] [text input] [🗑️]
├─ Rule 2: [doesn't contain ▼] [text input] [🗑️]
└─ Rule 3: [contains ▼] [text input] [🗑️]
───────────────────────────────────────────────────
Group 2
├─ [Rules Logic: OR ▼] [➕ Add Rule] [🗑️ Group]
├─ Rule 1: [contains ▼] [text input] [🗑️]
└─ Rule 2: [contains ▼] [text input] [🗑️]
───────────────────────────────────────────────────
```

## Usage Examples

### Example 1: Simple Contains Filter
**Goal**: Select all campaigns containing "Brand"

**Setup**:
- Add Filter Group
  - Rule 1: `contains` → "Brand"

**Result**: All campaigns with "Brand" in the name

---

### Example 2: Exclude Multiple Terms (AND Logic)
**Goal**: Campaigns that DON'T contain "Branded" AND DON'T contain "Test"

**Setup**:
- Add Filter Group
  - Rules Logic: **AND**
  - Rule 1: `doesn't contain` → "Branded"
  - Rule 2: `doesn't contain` → "Test"

**Result**: Only campaigns without "Branded" OR "Test" in their name

---

### Example 3: Include Multiple Terms (OR Logic)
**Goal**: Campaigns containing "Product A" OR "Product B"

**Setup**:
- Add Filter Group
  - Rules Logic: **OR**
  - Rule 1: `contains` → "Product A"
  - Rule 2: `contains` → "Product B"

**Result**: Campaigns with either term

---

### Example 4: Complex Multi-Group (AND Between Groups)
**Goal**: Campaigns that contain "Non" AND contain either "Auto" OR "Manual"

**Setup**:
- Between Groups: **AND**
- Group 1:
  - Rule 1: `contains` → "Non"
- Group 2:
  - Rules Logic: **OR**
  - Rule 1: `contains` → "Auto"
  - Rule 2: `contains` → "Manual"

**Result**: Campaigns like:
- ✅ "Non-Branded Auto Campaign"
- ✅ "Non-Branded Manual Campaign"
- ❌ "Non-Branded Exact Campaign" (doesn't match Group 2)
- ❌ "Branded Auto Campaign" (doesn't match Group 1)

---

### Example 5: Complex Multi-Group (OR Between Groups)
**Goal**: Campaigns that (contain "High Priority" AND "Active") OR (contain "Urgent")

**Setup**:
- Between Groups: **OR**
- Group 1:
  - Rules Logic: **AND**
  - Rule 1: `contains` → "High Priority"
  - Rule 2: `contains` → "Active"
- Group 2:
  - Rule 1: `contains` → "Urgent"

**Result**: Campaigns like:
- ✅ "High Priority Active Campaign" (matches Group 1)
- ✅ "Urgent Campaign" (matches Group 2)
- ✅ "High Priority Active Urgent" (matches both)
- ❌ "High Priority Paused" (doesn't match any group completely)

---

### Example 6: Advanced Exclusion Pattern
**Goal**: All campaigns EXCEPT those containing "Branded" or "Test"

**Setup**:
- Add Filter Group
  - Rules Logic: **AND**
  - Rule 1: `doesn't contain` → "Branded"
  - Rule 2: `doesn't contain` → "Test"

**Result**: Only campaigns without either exclusion term

---

### Example 7: Product Family Selection
**Goal**: Campaigns for Product Line A or Product Line B, but exclude test campaigns

**Setup**:
- Between Groups: **AND**
- Group 1 (Select Product Lines):
  - Rules Logic: **OR**
  - Rule 1: `contains` → "Product Line A"
  - Rule 2: `contains` → "Product Line B"
- Group 2 (Exclude Tests):
  - Rule 1: `doesn't contain` → "Test"

**Result**: Product campaigns without test variants

---

## Logic Truth Tables

### AND Logic (All Must Match)
| Rule 1 | Rule 2 | Result |
|--------|--------|--------|
| ✅ Match | ✅ Match | ✅ **Pass** |
| ✅ Match | ❌ No Match | ❌ **Fail** |
| ❌ No Match | ✅ Match | ❌ **Fail** |
| ❌ No Match | ❌ No Match | ❌ **Fail** |

### OR Logic (At Least One Must Match)
| Rule 1 | Rule 2 | Result |
|--------|--------|--------|
| ✅ Match | ✅ Match | ✅ **Pass** |
| ✅ Match | ❌ No Match | ✅ **Pass** |
| ❌ No Match | ✅ Match | ✅ **Pass** |
| ❌ No Match | ❌ No Match | ❌ **Fail** |

## Filter Results Display

### When Filters Match Campaigns
```
✅ 47 campaigns match your filters
[Add All Filtered Campaigns]
```
- Shows real-time count of matching campaigns
- Button to add all filtered campaigns to selection

### When No Campaigns Match
```
⚠️ No campaigns match your filter criteria
```
- Warning indicator
- No campaigns available for selection

## Workflow

### Step 1: Add Filter Group
Click **"➕ Add Filter Group"** to create a new group

### Step 2: Configure Group Logic
Select **AND** or **OR** for how rules combine within the group

### Step 3: Add Rules
- Click **"➕ Add Rule"** to add more conditions
- Select condition: `contains` or `doesn't contain`
- Enter search text (case-insensitive)

### Step 4: Add More Groups (Optional)
- Click **"➕ Add Filter Group"** to add additional groups
- Configure **"Between Groups"** logic (AND/OR)

### Step 5: Review Results
- See real-time count: "✅ X campaigns match your filters"
- Click **"Add All Filtered Campaigns"** to bulk-add them

### Step 6: Manage Filters
- **🗑️** next to rule: Remove individual rule
- **🗑️ Group**: Remove entire group
- **Clear All**: Remove all groups and start over

## Best Practices

### 1. Start Simple
Begin with a single group and add complexity as needed

### 2. Use OR for Alternatives
When selecting campaigns across multiple categories:
```
Group: OR logic
- contains "Category A"
- contains "Category B"
- contains "Category C"
```

### 3. Use AND for Refinement
When narrowing down with multiple criteria:
```
Group: AND logic
- contains "High Performance"
- doesn't contain "Paused"
```

### 4. Combine Groups for Precision
Use multiple groups with AND/OR between them for surgical precision:
```
Between Groups: AND
Group 1 (Include): contains "Target Keyword"
Group 2 (Exclude): doesn't contain "Branded"
```

### 5. Test Iteratively
- Add one rule at a time
- Check the results count after each addition
- Adjust logic operators if results don't match expectations

### 6. Use "Doesn't Contain" Carefully
Remember: `doesn't contain "X"` matches campaigns that lack "X"
- Multiple "doesn't contain" with AND = stricter exclusion
- Multiple "doesn't contain" with OR = broader exclusion

## Technical Details

### Matching Behavior
- **Case-insensitive**: "brand", "Brand", "BRAND" all match
- **Substring matching**: "Auto" matches "Automatic Campaign"
- **Empty rules ignored**: Blank text inputs don't affect results

### Performance
- Real-time filtering (no lag)
- Efficient for hundreds of campaigns
- Results update immediately on changes

### Persistence
- Filter groups persist within the session
- Reset on page refresh
- Separate filters for "Branded Terms" and "Pasted List" sections

## Troubleshooting

### Issue: No campaigns match but I expect results
**Solution**: 
- Check that conditions are correct (`contains` vs `doesn't contain`)
- Verify text spelling and spacing
- Try OR logic if using AND

### Issue: Too many campaigns match
**Solution**:
- Add more restrictive rules with AND logic
- Add exclusion rules (`doesn't contain`)
- Create additional groups with AND between groups

### Issue: Filter shows 0 campaigns after adding group
**Solution**:
- Check **Between Groups** logic - AND requires matching ALL groups
- Verify each group has at least one non-empty rule
- Try switching to OR logic between groups

## Integration

### Works With
- ✅ "Select All Enabled Non-Branded Campaigns" button
- ✅ "Clear Campaign Selection" button
- ✅ Manual multiselect dropdown
- ✅ All campaign types (SP, SB, SD)
- ✅ Both "Branded Terms" and "Pasted List" sections

### Independent From
- Campaign-level negatives (operates before selection)
- Ad group-level negatives (operates before selection)
- Negative keywords queue (operates before addition)

## Visual Example Flow

```
1. User clicks "Add Filter Group"
   → Empty group with one rule appears

2. User configures:
   - Rule 1: contains "Non-Branded"
   - Clicks "Add Rule"
   - Rule 2: doesn't contain "Test"
   - Group Logic: AND

3. Real-time results:
   "✅ 23 campaigns match your filters"

4. User clicks "Add Filter Group" (second group)
   - Rule 1: contains "High ROAS"
   - Between Groups: OR

5. Updated results:
   "✅ 31 campaigns match your filters"

6. User clicks "Add All Filtered Campaigns"
   → All 31 campaigns added to selection

7. User clicks "Add Branded Negatives"
   → Branded terms added to all 31 campaigns
```

## Benefits

### Precision
- Target exact campaign sets without manual selection
- Avoid mistakes from manual picking

### Efficiency
- Bulk-select hundreds of campaigns instantly
- Save time on repetitive campaign selection

### Flexibility
- Handle simple and complex filtering needs
- Adapt to any campaign naming convention

### Transparency
- See exactly which campaigns match
- Understand logic with visual group structure

### Reusability
- Set up filters once, use multiple times
- Clear and rebuild when needed
