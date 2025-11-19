# Filter Groups - Quick Reference

## Buttons

| Button | Action |
|--------|--------|
| **➕ Add Filter Group** | Create new group |
| **➕ Add Rule** | Add rule to current group |
| **🗑️** (next to rule) | Delete that rule |
| **🗑️ Group** | Delete entire group |
| **Clear All** | Remove all groups |
| **Add All Filtered Campaigns** | Bulk-add matching campaigns |

## Logic Operators

### Rules Logic (Within Group)
- **AND** = Campaign must match **ALL rules** in group
- **OR** = Campaign must match **ANY rule** in group

### Between Groups Logic
- **AND** = Campaign must match **ALL groups**
- **OR** = Campaign must match **ANY group**

## Conditions

| Condition | Behavior |
|-----------|----------|
| **contains** | Campaign name includes the text |
| **doesn't contain** | Campaign name excludes the text |

## Common Patterns

### ✅ Select campaigns with term
```
Group: contains "keyword"
```

### ❌ Exclude campaigns with term
```
Group: doesn't contain "keyword"
```

### ✅ OR ✅ Select campaigns with either term
```
Group (OR logic):
  - contains "term A"
  - contains "term B"
```

### ✅ AND ✅ Select campaigns with both terms
```
Group (AND logic):
  - contains "term A"
  - contains "term B"
```

### ✅ NOT (❌ OR ❌) Exclude multiple terms
```
Group (AND logic):
  - doesn't contain "term A"
  - doesn't contain "term B"
```

### (✅ OR ✅) AND ❌ Include terms but exclude another
```
Between Groups: AND

Group 1 (OR logic):
  - contains "term A"
  - contains "term B"

Group 2:
  - doesn't contain "exclude term"
```

## Examples by Use Case

### Select Non-Branded Campaigns
```
Group: contains "Non"
```

### Select Auto or Manual Campaigns
```
Group (OR logic):
  - contains "Auto"
  - contains "Manual"
```

### Exclude Test and Paused Campaigns
```
Group (AND logic):
  - doesn't contain "Test"
  - doesn't contain "Paused"
```

### Select Product Line A or B, Exclude Tests
```
Between Groups: AND

Group 1 (OR logic):
  - contains "Product A"
  - contains "Product B"

Group 2:
  - doesn't contain "Test"
```

### Select High-Priority Active Campaigns
```
Group (AND logic):
  - contains "High Priority"
  - contains "Active"
```

## Tips

1. **Match count updates live** - See results instantly
2. **Case-insensitive** - "brand" = "Brand" = "BRAND"
3. **Empty rules ignored** - Blank text doesn't affect filtering
4. **Start simple** - Add complexity gradually
5. **Test each step** - Check match count after each rule

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No matches | Use OR instead of AND |
| Too many matches | Add exclusion rules with AND |
| Unexpected results | Check "Between Groups" logic |
| Filter not working | Ensure rules have text entered |

## Keyboard Workflow

1. Click "Add Filter Group"
2. Type search text → Enter
3. Click "Add Rule" (if needed)
4. Type next text → Enter
5. Review match count
6. Click "Add All Filtered Campaigns"
7. Proceed with negative keyword addition
