# Sponsored Display Campaigns Report

## Complete Column List

**Note:** Use `Campaign Name (Informational only)` and `Ad Group Name (Informational only)` for reading campaign/ad group names. Use `Campaign Name` and `Ad Group Name` only when *editing* these values via bulk upload.

### Identifiers & Structure
- **Product**: Type of ad product (Sponsored Display)
- **Entity**: Type of row entry (Campaign, Ad Group, Ad, Targeting, etc.)
- **Campaign ID**: Unique campaign identifier
- **Portfolio ID**: Associated portfolio identifier (if any)
- **Ad Group ID**: Unique ad group identifier
- **Ad ID**: Unique ad identifier
- **Targeting ID**: Unique targeting clause identifier

### Naming & Dates
- **Campaign Name**: *For editing only*
- **Ad Group Name**: *For editing only*
- **Campaign Name (Informational only)**: Campaign name for reading (case-insensitive)
- **Ad Group Name (Informational only)**: Ad group name for reading (case-insensitive)
- **Portfolio Name (Informational only)**: Portfolio name
- **Start Date**: Campaign/item start date
- **End Date**: Campaign/item end date (if applicable)

### Status & Settings
- **Operation**: Action for bulk upload (Create, Update, Archive)
- **State**: Current status (enabled, paused, archived)
- **Campaign State (Informational only)**: Read-only campaign status
- **Ad Group State (Informational only)**: Read-only ad group status
- **Tactic**: Campaign tactic (e.g., T00020 - Contextual targeting)
- **Budget Type**: Daily/Lifetime
- **Budget**: Budget amount
- **SKU**: Associated product SKU
- **ASIN**: Associated product ASIN
- **Ad Group Default Bid**: Default bid for the ad group
- **Ad Group Default Bid (Informational only)**: Read-only default bid
- **Bid**: Specific bid for targeting
- **Bid Optimization**: Strategy used (e.g., Optimize for page visits)
- **Cost Type**: CPC/vCPM

### Targeting
- **Targeting Expression**: Targeting criteria (e.g., `audienceId=123` or `asinCategorySameAs="B0..."`)
- **Resolved Targeting Expression (Informational only)**: Expanded targeting

### Performance Metrics (Calculated)
- **Impressions**: Ad views
- **Clicks**: Ad clicks
- **Click-through Rate (CTR)**: Clicks ÷ Impressions
- **Spend**: Total ad cost
- **Sales**: Total click-attributed sales
- **Orders**: Number of click-attributed orders
- **Units**: Number of click-attributed units sold
- **Conversion Rate**: Orders ÷ Clicks
- **ACOS (Advertising Cost of Sale)**: Spend ÷ Sales
- **CPC (Cost Per Click)**: Spend ÷ Clicks
- **ROAS (Return on Ad Spend)**: Sales ÷ Spend

### View-Specific Metrics (Calculated)
- **Viewable Impressions**: Impressions meeting viewability standards
- **Sales (Views & Clicks)**: Total sales attributed to both views and clicks
- **Orders (Views & Clicks)**: Total orders attributed to both views and clicks
- **Units (Views & Clicks)**: Total units attributed to both views and clicks
- **ACOS (Views & Clicks)**: Spend ÷ Sales (Views & Clicks)
- **ROAS (Views & Clicks)**: Sales (Views & Clicks) ÷ Spend
