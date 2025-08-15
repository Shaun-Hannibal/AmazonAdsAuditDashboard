# Sponsored Products Campaigns Report

## Complete Column List

**Note:** Use `Campaign Name (Informational only)` and `Ad Group Name (Informational only)` for reading campaign/ad group names. Use `Campaign Name` and `Ad Group Name` only when *editing* these values via bulk upload.

### Identifiers & Structure
- **Product**: Type of ad product (Sponsored Products)
- **Entity**: Type of row entry (Campaign, Ad Group, Keyword, etc.)
- **Campaign ID**: Unique campaign identifier
- **Ad Group ID**: Unique ad group identifier
- **Portfolio ID**: Associated portfolio identifier (if any)
- **Ad ID**: Unique ad identifier
- **Keyword ID**: Unique keyword identifier
- **Product Targeting ID**: Unique targeting identifier

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
- **Daily Budget**: Campaign daily budget amount
- **SKU**: Associated product SKU. Use for Seller Central account
- **ASIN**: Associated product ASIN. Use for Vendor Central account
- **Eligibility Status (Informational only)**: If ad is eligible to run
- **Reason for Ineligibility (Informational only)**: Reason if ineligible
- **Ad Group Default Bid**: Default bid for the ad group
- **Ad Group Default Bid (Informational only)**: Read-only default bid
- **Bid**: Specific bid for keyword/targeting
- **Bidding Strategy**: Bidding approach (e.g., Dynamic bids - down only)
- **Placement**: Ad placement (e.g., Top of search (first page))
- **Percentage**: Bid adjustment percentage for placement

### Targeting
- **Targeting Type**: Auto/Manual
- **Keyword Text**: Targeted keyword
- **Native Language Keyword**: Keyword in original language
- **Native Language Locale**: Locale of native language keyword
- **Match Type**: Broad/Phrase/Exact/Negative
- **Product Targeting Expression**: Targeting criteria (e.g., `asin="B0..."`)
- **Resolved Product Targeting Expression (Informational only)**: Expanded targeting

### Performance Metrics (Calculated)
- **Impressions**: Times ads were shown
- **Clicks**: Clicks on ads
- **Click-through Rate (CTR)**: Clicks ÷ Impressions
- **Spend**: Total ad cost
- **Sales**: Total sales attributed to ads (within attribution window)
- **Orders**: Number of orders attributed
- **Units**: Number of units sold attributed
- **Conversion Rate**: Orders ÷ Clicks
- **ACOS (Advertising Cost of Sale)**: Spend ÷ Sales
- **CPC (Cost Per Click)**: Spend ÷ Clicks
- **ROAS (Return on Ad Spend)**: Sales ÷ Spend
