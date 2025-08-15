import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import io
import re
import altair as alt

def remove_hyperlinks_from_df(df):
    url_pattern = re.compile(r'https?://\S+')
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).apply(lambda x: url_pattern.sub('', x))
    return df

def classify_branding(campaign_name):
    """Classifies campaign branding based on keywords in Campaign Name."""
    if pd.isna(campaign_name):
        return "Unknown"
    campaign_name_lower = str(campaign_name).lower()
    # Prioritize 'Non-Branded' if 'Non' is present, even if 'Brand' is also present
    if "non" in campaign_name_lower: # Catches 'non-brand', 'non brand', 'nonbranded'
        return "Non-Branded"
    elif "brand" in campaign_name_lower: # Catches 'brand', 'branded'
        return "Branded"
    else: # Default if neither specific keyword is found
        return "Non-Branded" 

st.set_page_config(page_title="Amazon Bid Optimizer", layout="wide")
st.title("Amazon Bid Optimizer")

# --- Session State Initialization ---
def init_state():
    if "df_dict" not in st.session_state:
        st.session_state.df_dict = None
    if "uploaded_file_name" not in st.session_state:
        st.session_state.uploaded_file_name = ""
    if "filters" not in st.session_state:
        # New structure: List of dicts with condition and logic type
        # Each condition is: {"column": col, "type": type, "value": val, "logic": "AND"}
        st.session_state.filters = []
    if "filter_groups" not in st.session_state:
        st.session_state.filter_groups = [] # List of tuples, each tuple is (filter_list, target_acos)_value) for finalized groups
    
    # Optimizer Settings
    if "target_acos" not in st.session_state:
        st.session_state.target_acos = "15" 
    if "increase_percent" not in st.session_state:
        st.session_state.increase_percent = "5" 
    if "decrease_percent" not in st.session_state:
        st.session_state.decrease_percent = "3" 
    if "adjust_based_on_increase" not in st.session_state:
        st.session_state.adjust_based_on_increase = "Orders"
    if "adjust_based_on_decrease" not in st.session_state:
        st.session_state.adjust_based_on_decrease = "Spend" 
    if "min_spend_threshold" not in st.session_state:
        st.session_state.min_spend_threshold = "" 

    # Analysis and File Upload
    if "analysis_data" not in st.session_state:
        st.session_state.analysis_data = {
            'increased': 0,
            'decreased': 0,
            'unchanged': 0,
            'total_rows': 0,
            'total_increase_amount': 0,  # Sum of positive bid changes
            'total_decrease_amount': 0,  # Sum of absolute negative bid changes
            'sp_count': 0,
            'sb_count': 0,
            'sd_count': 0,
            'vcpm_count': 0,
            'total_spend': 0,
            'total_sales': 0,
            'total_clicks': 0,
            'total_impressions': 0,
            'increased_by_0_10': 0,
            'increased_by_10_25': 0,
            'increased_by_25_50': 0,
            'increased_by_50_plus': 0,
            'decreased_by_0_10': 0,
            'decreased_by_10_25': 0,
            'decreased_by_25_50': 0,
            'decreased_by_50_plus': 0,
            'avg_old_bid': 0, # Will store sum of old bids; average calculated in UI
            'avg_new_bid': 0, # Will store sum of new bids; average calculated in UI
            'current_acos': 0, # Overall, calculated as total_spend / total_sales in UI
            'projected_acos': 0, # Overall, calculated as projected_total_spend / projected_total_sales in UI

            # New Overall Projections
            'projected_total_spend': 0,
            'projected_total_sales': 0,
            'projected_total_clicks': 0,

            # New Branding Metrics
            'branded_total_rows': 0, 'non_branded_total_rows': 0, 'unknown_total_rows': 0,
            'branded_increased_bids': 0, 'non_branded_increased_bids': 0, 'unknown_increased_bids': 0,
            'branded_decreased_bids': 0, 'non_branded_decreased_bids': 0, 'unknown_decreased_bids': 0,
            'branded_unchanged_bids': 0, 'non_branded_unchanged_bids': 0, 'unknown_unchanged_bids': 0,

            'branded_current_spend': 0, 'non_branded_current_spend': 0, 'unknown_current_spend': 0,
            'branded_current_sales': 0, 'non_branded_current_sales': 0, 'unknown_current_sales': 0,
            'branded_current_clicks': 0, 'non_branded_current_clicks': 0, 'unknown_current_clicks': 0,
            # ACoS for branded categories will be calculated in the UI

            'branded_projected_spend': 0, 'non_branded_projected_spend': 0, 'unknown_projected_spend': 0,
            'branded_projected_sales': 0, 'non_branded_projected_sales': 0, 'unknown_projected_sales': 0,
            'branded_projected_clicks': 0, 'non_branded_projected_clicks': 0, 'unknown_projected_clicks': 0,
            # Projected ACoS for branded categories will be calculated in the UI
            
            'branded_sum_old_bids': 0, 'non_branded_sum_old_bids': 0, 'unknown_sum_old_bids': 0,
            'branded_sum_new_bids': 0, 'non_branded_sum_new_bids': 0, 'unknown_sum_new_bids': 0,
            'branded_bid_count': 0, 'non_branded_bid_count': 0, 'unknown_bid_count': 0, # For calculating avg bids per brand type

            # New Campaign Type Metrics (beyond just counts)
            'sp_current_spend': 0, 'sb_current_spend': 0, 'sd_current_spend': 0,
            'sp_current_sales': 0, 'sb_current_sales': 0, 'sd_current_sales': 0,
            'sp_current_clicks': 0, 'sb_current_clicks': 0, 'sd_current_clicks': 0,
            # Current ACoS for campaign types will be calculated in the UI

            'sp_projected_spend': 0, 'sb_projected_spend': 0, 'sd_projected_spend': 0,
            'sp_projected_sales': 0, 'sb_projected_sales': 0, 'sd_projected_sales': 0,
            'sp_projected_clicks': 0, 'sb_projected_clicks': 0, 'sd_projected_clicks': 0,
            # Projected ACoS for campaign types will be calculated in the UI

            # Top Movers (holding up to N items, e.g., 10)
            'top_bid_increases': [], 
            'top_bid_decreases': [] 
        }
    if "uploaded_file_name" not in st.session_state:
        st.session_state.uploaded_file_name = ""
    if "df_dict" not in st.session_state:
        st.session_state.df_dict = None
    if "keyword_projections" not in st.session_state:
        st.session_state.keyword_projections = []
init_state()

# Ensure critical session state variables are initialized
if 'min_spend_threshold' not in st.session_state:
    st.session_state.min_spend_threshold = ""

# --- Helper Functions ---
def format_currency(num):
    try:
        return f"${num:,.2f}"
    except:
        return str(num)

def format_number(num):
    try:
        return f"{num:,.0f}"
    except:
        return str(num)

def apply_filters(df, default_target_acos, filter_groups):
    # Set default Target ACoS
    df['Target ACoS'] = default_target_acos
    
    # Apply each filter group
    for group_filters, group_acos in filter_groups:
        # Determine which filter format is being used
        if len(group_filters) > 0 and isinstance(group_filters[0], dict):  # New format with explicit logic
            group_mask = process_mixed_logic_filters(df, group_filters)
        else:  # Old format with implicit AND logic
            # Start with all True for this group
            group_mask = pd.Series([True] * len(df))
            
            # Apply each filter in the group (AND within group)
            for col, filter_type, val in group_filters:
                mask = create_filter_mask(df, col, filter_type, val)
                # AND this filter with the current group mask
                group_mask = group_mask & mask
        
        # Apply the group's target ACoS to matching rows
        if group_mask.any():
            df.loc[group_mask, 'Target ACoS'] = group_acos
    
    return df

# Helper function to process filters with mixed AND/OR logic
def process_mixed_logic_filters(df, filters):
    if not filters:
        return pd.Series([True] * len(df))
    
    # Start with the first condition
    result_mask = create_filter_mask(df, filters[0]["column"], filters[0]["type"], filters[0]["value"])
    
    # Process remaining conditions with their specified logic
    for i in range(1, len(filters)):
        condition = filters[i]
        current_mask = create_filter_mask(df, condition["column"], condition["type"], condition["value"])
        
        if condition["logic"] == "AND":
            result_mask = result_mask & current_mask
        elif condition["logic"] == "OR":
            result_mask = result_mask | current_mask
    
    return result_mask

# Helper function to create a filter mask based on column, type and value
def create_filter_mask(df, col, filter_type, val):
    # Special case for Campaign Name - look for Campaign Name (Informational Only) column
    actual_col = col
    if col == 'Campaign Name':
        # Find the Campaign Name (Informational Only) column using case-insensitive search
        info_col = next((c for c in df.columns if 'campaign name' in c.lower() and 'informational' in c.lower()), None)
        if info_col:
            actual_col = info_col
    
    # Check if the actual column exists in the dataframe
    if actual_col not in df.columns:
        return pd.Series([True] * len(df))
        
    if filter_type == "equals":
        mask = df[actual_col] == val
    elif filter_type == "contains":
        mask = df[actual_col].astype(str).str.contains(val, case=False, na=False)
    elif filter_type == "greater than":
        try:
            mask = df[actual_col] > float(val)
        except:
            mask = pd.Series([False] * len(df))
    elif filter_type == "less than":
        try:
            mask = df[actual_col] < float(val)
        except:
            mask = pd.Series([False] * len(df))
    elif filter_type == "doesn't contain":
        mask = ~df[actual_col].astype(str).str.contains(val, case=False, na=False)
    elif filter_type == "doesn't equal":
        mask = df[actual_col] != val
    elif filter_type == "less than or equal to":
        try:
            mask = df[actual_col] <= float(val)
        except:
            mask = pd.Series([False] * len(df))
    elif filter_type == "greater than or equal to":
        try:
            mask = df[actual_col] >= float(val)
        except:
            mask = pd.Series([False] * len(df))
    else:
        # Unknown filter type
        mask = pd.Series([True] * len(df))
    
    return mask

def apply_guardrails(df, increase_percent, decrease_percent, adjust_based_on_increase, adjust_based_on_decrease):
    # Calculate recommended bid based on EQ Bid
    df['Recommended Bid'] = df['EQ Bid']
    # Use VCPM as the base bid if it's a VCPM campaign, otherwise use CPC
    is_vcpm_campaign = (df['Type'] == 'VCPM') | (pd.notna(df['VCPM']))
    df['Base Bid'] = np.where(is_vcpm_campaign, df['VCPM'], df['CPC'])

    if adjust_based_on_increase and adjust_based_on_increase in df.columns:
        factor = {
            "Clicks": df['Clicks'],
            "Spend": df['Spend'] / 100,
            "Orders": df['Orders']
        }[adjust_based_on_increase]
        df['Max Increase Limit'] = df['Base Bid'] * (1 + increase_percent * factor)
    else:
        df['Max Increase Limit'] = df['Base Bid']

    if adjust_based_on_decrease and adjust_based_on_decrease in df.columns:
        factor = {
            "Clicks": df['Clicks'],
            "Spend": df['Spend'],
            "Orders": df['Orders']
        }[adjust_based_on_decrease]
        df['Min Decrease Limit'] = df['Base Bid'] * (1 - decrease_percent * factor)
    else:
        df['Min Decrease Limit'] = df['Base Bid']

    df['Recommended Bid'] = np.where(
        (df['EQ Bid'] == 0) & (df['Spend'] > 0),
        np.maximum(df['Base Bid'] * (1 - decrease_percent * df['Spend']), df['Min Decrease Limit']),
        np.where(
            df['EQ Bid'] < df['Min Decrease Limit'],
            df['Min Decrease Limit'],
            np.where(
                df['EQ Bid'] > df['Max Increase Limit'],
                df['Max Increase Limit'],
                df['EQ Bid']
            )
        )
    )
    
    # New condition: if both 'EQ Bid' and 'Old Bid' are lower than 'Recommended Bid',
    # cap 'Recommended Bid' at 'Old Bid'.
    # This check occurs before the 'Recommended Bid' is moved to the 'Bid' column in process_sheet.
    condition_both_lower = (df['EQ Bid'] < df['Recommended Bid']) & (df['Old Bid'] < df['Recommended Bid'])
    df['Recommended Bid'] = np.where(
        condition_both_lower,
        df['Old Bid'],
        df['Recommended Bid']
    )

    return df

def process_sheet(df, default_target_acos, increase_percent, decrease_percent, adjust_based_on_increase, adjust_based_on_decrease, filter_groups, min_spend_threshold=None, sd_vcpm_metric='Sales'):
    # Make a copy of the dataframe to avoid modifying the original
    df = df.copy()
    # Strip whitespace from all column names
    df.columns = df.columns.str.strip()
    # Ensure 'State' column exists after cleaning
    if 'State' not in df.columns:
        raise KeyError(f"'State' column not found in the uploaded file. Columns found: {list(df.columns)}. Please check for typos or extra spaces in column headers.")
    # Check if this is a Sponsored Brands sheet by looking for indicators in the columns or data
    is_sponsored_brands = False
    if 'Product' in df.columns:
        is_sponsored_brands = df['Product'].astype(str).str.lower().eq('sponsored brands').any()
    # Filter active campaigns with valid bids
    df = df[df['State'].astype(str).str.lower() == "enabled"].dropna(subset=['Bid']).copy()
    # For Sponsored Brands, keep rows with either clicks > 0 or impressions > 1000
    if is_sponsored_brands:
        df = df[(df['Clicks'] > 0) | (df.get('Impressions', 0) > 1000)].copy()
    else:
        df = df[df['Clicks'] > 0].copy()
    # Apply minimum spend filter if set
    if min_spend_threshold is not None:
        df = df[df['Spend'] >= min_spend_threshold]
    # Determine campaign type
    camp_col = next((col for col in df.columns if col.lower() == 'campaign name (informational only)'), None)
    if camp_col:
        df['Type'] = np.where(df[camp_col].astype(str).str.contains("VCPM", case=False, na=False), "VCPM", "Other")
    if 'Product' in df.columns and 'Cost Type' in df.columns:
        df['Type'] = np.where((df['Product'].astype(str).str.lower() == 'sponsored display') & (df['Cost Type'].astype(str).str.lower() == 'vcpm'), 'VCPM', df['Type'])
    # Ensure 'Bid' is numeric and store as 'Old Bid'
    df['Bid'] = pd.to_numeric(df['Bid'], errors='coerce').fillna(0)
    df['Old Bid'] = df['Bid']
    # Ensure 'VCPM' column exists and is numeric
    if 'VCPM' not in df.columns:
        df['VCPM'] = np.nan
    df['VCPM'] = pd.to_numeric(df['VCPM'], errors='coerce')
    # Calculate VCPM if not provided
    if 'Type' in df.columns and 'Spend' in df.columns:
        if 'Viewable Impressions' in df.columns and df['Product'].astype(str).str.lower().eq('sponsored display').any():
            df['VCPM'] = np.where(
                (df['Type'] == 'VCPM') & (df['Product'].astype(str).str.lower() == 'sponsored display') & (pd.isna(df['VCPM'])),
                (df['Spend'] / (df['Viewable Impressions'] / 1000)).round(2),
                df['VCPM']
            )
        elif 'Impressions' in df.columns:
            df['VCPM'] = np.where(
                (df['Type'] == 'VCPM') & (pd.isna(df['VCPM'])),
                (df['Spend'] / (df['Impressions'] / 1000)).round(2),
                df['VCPM']
            )
    # Apply filters
    df = apply_filters(df, default_target_acos, filter_groups)
    # Calculate Current ACoS for VCPM campaigns
    df['Current ACoS'] = np.where(
        df['Sales'] > 0,
        df['Spend'] / df['Sales'],
        np.inf  # Avoid division by zero; will handle in EQ Bid calculation
    )
    # Calculate EQ Bid
    sales_col = 'Sales' if sd_vcpm_metric == "Sales" else 'Sales (Views & Clicks)'
    is_vcpm_campaign = (df['Type'] == 'VCPM') | (pd.notna(df['VCPM']))
    df['EQ Bid'] = np.where(
        is_vcpm_campaign,
        np.where(
            df['Current ACoS'] != np.inf,
            df['VCPM'] * (df['Target ACoS'] / df['Current ACoS']),
            0
        ),
        np.where(
            (df['Clicks'] > 0) & (df['Sales'] == 0),
            0,
            np.where(
                (df['Clicks'] > 0),
                (df['Target ACoS'] * df['Sales']) / df['Clicks'],
                df.get('CPC', np.nan)
            )
        )
    )
    # Apply guardrails
    df = apply_guardrails(df, increase_percent, decrease_percent, adjust_based_on_increase, adjust_based_on_decrease)
    
    # --- Branding Classification ---
    camp_col_name = next((col for col in df.columns if col.lower() == 'campaign name (informational only)'), None)
    if camp_col_name:
        df['Branding_Category'] = df[camp_col_name].apply(classify_branding)
    else:
        df['Branding_Category'] = 'Unknown' # Default if campaign name column is missing

    # --- Row-Level Performance Projections ---
    # Ensure Old Bid and Recommended Bid are numeric before calculations
    df['Old Bid'] = pd.to_numeric(df['Old Bid'], errors='coerce').fillna(0)
    df['Recommended Bid'] = pd.to_numeric(df['Recommended Bid'], errors='coerce').fillna(0)
    df['Clicks'] = pd.to_numeric(df['Clicks'], errors='coerce').fillna(0)
    df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce').fillna(0)
    df['Spend'] = pd.to_numeric(df['Spend'], errors='coerce').fillna(0)
    # Target ACoS is already applied to df['Target ACoS'] by apply_filters
    df['Target ACoS'] = pd.to_numeric(df['Target ACoS'], errors='coerce').fillna(0)

    # Ensure correct types before projections
    df['Old Bid'] = pd.to_numeric(df['Old Bid'], errors='coerce').fillna(0)
    df['Recommended Bid'] = pd.to_numeric(df['Recommended Bid'], errors='coerce').fillna(0)
    df['Clicks'] = pd.to_numeric(df['Clicks'], errors='coerce').fillna(0)
    df['Target ACoS'] = pd.to_numeric(df['Target ACoS'], errors='coerce').fillna(0)

    # Calculate Bid_Change_Ratio carefully to handle zero values
    # Default to 1.0 (no change factor) for cases like Old Bid == 0, Rec Bid > 0
    # or if both are equal and positive.
    df['Bid_Change_Ratio'] = 1.0

    # Case 1: Old Bid > 0 and Rec Bid > 0
    mask_old_bid_pos_rec_bid_pos = (df['Old Bid'] > 0) & (df['Recommended Bid'] > 0)
    df.loc[mask_old_bid_pos_rec_bid_pos, 'Bid_Change_Ratio'] = \
        df['Recommended Bid'] / df['Old Bid']

    # Case 2: Old Bid > 0 and Rec Bid == 0 (or <0)
    mask_old_bid_pos_rec_bid_zero = (df['Old Bid'] > 0) & (df['Recommended Bid'] <= 0)
    df.loc[mask_old_bid_pos_rec_bid_zero, 'Bid_Change_Ratio'] = 0.0

    # Case 3: Old Bid == 0 and Rec Bid > 0 - Bid_Change_Ratio remains 1.0 (keeps current clicks)
    # Case 4: Old Bid == 0 and Rec Bid == 0 - Bid_Change_Ratio remains 1.0,
    #         but if Clicks are 0, Est New Clicks will be 0.
    #         If Clicks > 0 (e.g. free clicks, other targeting), Clicks * 1.0 is maintained.
    #         Est New Spend will be Clicks * 0 = 0.

    # Calculate average CPC for each row
    df['Current_CPC'] = np.where(df['Clicks'] > 0, df['Spend'] / df['Clicks'], df['Old Bid'])
    
    # Apply non-linear model for click changes with diminishing returns
    # For bid increases: use cube root for diminishing returns (slower growth)
    # For bid decreases: use square root for less dramatic drops (more conservative)
    df['Bid_Change_Ratio'] = np.maximum(df['Bid_Change_Ratio'], 0)  # Ensure non-negative
    
    # Different elasticity for increases vs decreases
    mask_increase = df['Bid_Change_Ratio'] > 1.0
    mask_decrease = df['Bid_Change_Ratio'] < 1.0
    mask_no_change = df['Bid_Change_Ratio'] == 1.0
    
    # Apply different elasticity models
    df.loc[mask_increase, 'Estimated_Click_Ratio'] = np.power(df.loc[mask_increase, 'Bid_Change_Ratio'], 1/3)  # Cube root for increases
    df.loc[mask_decrease, 'Estimated_Click_Ratio'] = np.power(df.loc[mask_decrease, 'Bid_Change_Ratio'], 1/2)  # Square root for decreases
    df.loc[mask_no_change, 'Estimated_Click_Ratio'] = 1.0  # No change
    
    # Calculate new clicks based on the elasticity model
    df['Estimated_New_Clicks'] = (df['Clicks'] * df['Estimated_Click_Ratio']).round(0)
    
    # Calculate new CPC - should decrease when bids decrease and increase when bids increase
    # But not in direct proportion to bid changes (elasticity factor)
    df['CPC_Change_Factor'] = np.where(
        mask_increase,
        np.power(df['Bid_Change_Ratio'], 0.7),  # CPC increases slower than bids for increases
        np.where(
            mask_decrease,
            np.power(df['Bid_Change_Ratio'], 0.9),  # CPC decreases slower than bids for decreases
            1.0  # No change
        )
    )
    
    # Calculate estimated new CPC
    df['Estimated_New_CPC'] = df['Current_CPC'] * df['CPC_Change_Factor']
    
    # Calculate new spend based on new clicks and new CPC (more accurate than using recommended bid directly)
    df['Estimated_New_Spend'] = (df['Estimated_New_Clicks'] * df['Estimated_New_CPC']).round(2)
    
    # Calculate conversion rate and sales per click for more accurate sales projections
    df['Conversion_Rate'] = np.where(df['Clicks'] > 0, df['Sales'] / (df['Clicks'] * df['Current_CPC']), 0)
    
    # Apply R-squared like correlation factor for sales projections
    # Higher spend doesn't always mean proportionally higher sales
    # Calculate elasticity factor for sales based on spend changes
    df['Spend_Change_Ratio'] = np.where(df['Spend'] > 0, df['Estimated_New_Spend'] / df['Spend'], 1.0)
    
    # Apply diminishing returns model for sales based on spend changes
    df['Sales_Elasticity'] = np.where(
        df['Spend_Change_Ratio'] > 1.0,
        np.power(df['Spend_Change_Ratio'], 0.6),  # Diminishing returns for spend increases
        np.where(
            df['Spend_Change_Ratio'] < 1.0,
            np.power(df['Spend_Change_Ratio'], 0.8),  # Less dramatic drops for spend decreases
            1.0  # No change
        )
    )
    
    # Calculate estimated new sales with the elasticity model
    df['Estimated_New_Sales'] = np.where(
        df['Target ACoS'] > 0,
        # If Target ACoS is available, use it but apply elasticity
        (df['Estimated_New_Spend'] / df['Target ACoS']) * 
        np.where(df['Estimated_New_Spend'] > df['Spend'], 0.9, 1.0),  # Slight discount for increased spend
        # Otherwise use the sales elasticity model
        (df['Sales'] * df['Sales_Elasticity'])
    ).round(2)
    
    # Ensure that if Target ACoS was zero, resulting sales are zero
    df.loc[df['Target ACoS'] == 0, 'Estimated_New_Sales'] = np.where(
        (df['Target ACoS'] == 0) & (df['Estimated_New_Spend'] > 0),
        0,  # Projected sales should be 0 (cannot meet 0 ACoS with spend)
        df['Estimated_New_Sales']  # Otherwise keep the already calculated sales
    ).round(2)
    
    # If no projected spend, no projected sales
    df.loc[df['Estimated_New_Spend'] == 0, 'Estimated_New_Sales'] = 0

    # Enforce minimum bids
    # Get the campaign name column
    camp_col = next((col for col in df.columns if col.lower() == 'campaign name (informational only)'), None)
    
    # Check for SBV or Video in campaign names if the column exists
    has_sbv_or_video = False
    if camp_col:
        has_sbv_or_video = df[camp_col].astype(str).str.contains('SBV|Video', case=False, na=False)
    
    # Ensure Product column is properly handled for string operations
    if 'Product' in df.columns:
        df['Product'] = df['Product'].astype(str).fillna('')
    else:
        df['Product'] = ''
    
    # Define conditions for different campaign types
    conditions = [
        # Sponsored Display conditions
        (df['Product'].str.lower() == 'sponsored display') & (is_vcpm_campaign),
        (df['Product'].str.lower() == 'sponsored display') & (~is_vcpm_campaign),
        
        # Sponsored Brand conditions with new criteria
        # 1. SB with SBV/Video and VCPM
        (df['Product'].str.lower() == 'sponsored brands') & (is_vcpm_campaign) & (has_sbv_or_video),
        # 2. SB with SBV/Video and not VCPM
        (df['Product'].str.lower() == 'sponsored brands') & (~is_vcpm_campaign) & (has_sbv_or_video),
        # 3. SB without SBV/Video and VCPM
        (df['Product'].str.lower() == 'sponsored brands') & (is_vcpm_campaign) & (~has_sbv_or_video),
        # 4. SB without SBV/Video and not VCPM
        (df['Product'].str.lower() == 'sponsored brands') & (~is_vcpm_campaign) & (~has_sbv_or_video),
        
        # Sponsored Products condition
        (df['Product'].str.lower() == 'sponsored products')
    ]
    
    # Define minimum bids for each condition
    min_bids = [
        1.00,  # SD with VCPM
        0.10,  # SD without VCPM
        12.00, # SB with SBV/Video and VCPM
        0.25,  # SB with SBV/Video and not VCPM
        8.00,  # SB without SBV/Video and VCPM
        0.10,  # SB without SBV/Video and not VCPM
        0.02   # SP
    ]
    
    # Apply minimum bids and round to 2 decimal places
    # First ensure Recommended Bid is numeric
    df['Recommended Bid'] = pd.to_numeric(df['Recommended Bid'], errors='coerce').fillna(0)
    df['Recommended Bid'] = df['Recommended Bid'].clip(lower=np.select(conditions, min_bids, default=0)).round(2)
    
    # Ensure 'Recommended Bid' and 'Old Bid' are numeric for analysis
    df['Recommended Bid'] = pd.to_numeric(df['Recommended Bid'], errors='coerce').fillna(0).round(2)
    df['Old Bid'] = pd.to_numeric(df['Old Bid'], errors='coerce').fillna(0).round(2)
    
    # Ensure 'ACoS' column exists
    if 'ACoS' not in df.columns:
        df['ACoS'] = np.where(df['Sales'] > 0, df['Spend'] / df['Sales'], np.nan)
    
    # Add Operation column if it doesn't exist
    if 'Operation' not in df.columns:
        df['Operation'] = ""
    
    # Update bids and operations
    df.loc[df['Recommended Bid'] != df['Old Bid'], 'Operation'] = "Update"
    df.loc[df['Operation'] == "Update", 'Bid'] = df['Recommended Bid']
    
    # Ensure final Bid column is properly rounded to 2 decimal places
    df['Bid'] = pd.to_numeric(df['Bid'], errors='coerce').fillna(0).round(2)
    
    # Create masks for increased, decreased, and unchanged bids
    increased_mask = (df['Recommended Bid'] > df['Old Bid']) & (df['Old Bid'] > 0)
    decreased_mask = (df['Recommended Bid'] < df['Old Bid']) & (df['Old Bid'] > 0)
    unchanged_mask = (df['Recommended Bid'] == df['Old Bid']) | (df['Old Bid'] == 0)
    
    # Update analysis data
    st.session_state.analysis_data['increased'] += increased_mask.sum()
    st.session_state.analysis_data['decreased'] += decreased_mask.sum()
    st.session_state.analysis_data['unchanged'] += unchanged_mask.sum()
    st.session_state.analysis_data['total_rows'] += len(df)
    
    # Sum of all old and new bids for overall average calculation in UI
    st.session_state.analysis_data['avg_old_bid'] += df['Old Bid'].sum()
    st.session_state.analysis_data['avg_new_bid'] += df['Recommended Bid'].sum()

    # Calculate differences for increases and decreases
    increase_diffs = (df['Recommended Bid'] - df['Old Bid']).where(increased_mask, 0)
    decrease_diffs = (df['Old Bid'] - df['Recommended Bid']).where(decreased_mask, 0)
    
    st.session_state.analysis_data['total_increase_amount'] += increase_diffs.sum()
    st.session_state.analysis_data['total_decrease_amount'] += decrease_diffs.sum()
    
    # Collect campaign type metrics
    if 'Product' in df.columns:
        # Product column is already converted to string and filled with empty strings above
        sp_count = (df['Product'].str.lower() == 'sponsored products').sum()
        sb_count = (df['Product'].str.lower() == 'sponsored brands').sum()
        sd_count = (df['Product'].str.lower() == 'sponsored display').sum()
        
        st.session_state.analysis_data['sp_count'] += sp_count
        st.session_state.analysis_data['sb_count'] += sb_count
        st.session_state.analysis_data['sd_count'] += sd_count
    
    # Count VCPM campaigns
    if 'Type' in df.columns:
        st.session_state.analysis_data['vcpm_count'] += (df['Type'] == 'VCPM').sum()
    
    # Create a mask for valid rows (Bid > 0.01)
    valid_rows_mask = df['Bid'] > 0.01
    
    # Collect performance metrics - only count rows where Bid > 0.01
    if 'Spend' in df.columns:
        st.session_state.analysis_data['total_spend'] += df.loc[valid_rows_mask, 'Spend'].sum()
    if 'Sales' in df.columns:
        st.session_state.analysis_data['total_sales'] += df.loc[valid_rows_mask, 'Sales'].sum()
    if 'Clicks' in df.columns:
        st.session_state.analysis_data['total_clicks'] += df.loc[valid_rows_mask, 'Clicks'].sum()
    if 'Impressions' in df.columns:
        st.session_state.analysis_data['total_impressions'] += df.loc[valid_rows_mask, 'Impressions'].sum()
    
    # --- Aggregate New Metrics for Branding and Campaign Types ---
    # Overall Projected Metrics - also only count rows where Bid > 0.01
    st.session_state.analysis_data['projected_total_spend'] += df.loc[valid_rows_mask, 'Estimated_New_Spend'].sum()
    st.session_state.analysis_data['projected_total_sales'] += df.loc[valid_rows_mask, 'Estimated_New_Sales'].sum()
    st.session_state.analysis_data['projected_total_clicks'] += df.loc[valid_rows_mask, 'Estimated_New_Clicks'].sum()

    branding_categories = ['Branded', 'Non-Branded', 'Unknown']
    for category in branding_categories:
        # Filter for both category and valid rows (Bid > 0.01)
        cat_df = df[(df['Branding_Category'] == category) & (df['Bid'] > 0.01)]
        cat_prefix = category.lower().replace('-', '_') + '_'

        st.session_state.analysis_data[cat_prefix + 'total_rows'] += len(cat_df)
        st.session_state.analysis_data[cat_prefix + 'increased_bids'] += (cat_df['Recommended Bid'] > cat_df['Old Bid']).sum()
        st.session_state.analysis_data[cat_prefix + 'decreased_bids'] += (cat_df['Recommended Bid'] < cat_df['Old Bid']).sum()
        st.session_state.analysis_data[cat_prefix + 'unchanged_bids'] += (cat_df['Recommended Bid'] == cat_df['Old Bid']).sum()

        st.session_state.analysis_data[cat_prefix + 'current_spend'] += cat_df['Spend'].sum()
        st.session_state.analysis_data[cat_prefix + 'current_sales'] += cat_df['Sales'].sum()
        st.session_state.analysis_data[cat_prefix + 'current_clicks'] += cat_df['Clicks'].sum()
        st.session_state.analysis_data[cat_prefix + 'sum_old_bids'] += cat_df['Old Bid'].sum()
        st.session_state.analysis_data[cat_prefix + 'sum_new_bids'] += cat_df['Recommended Bid'].sum()
        st.session_state.analysis_data[cat_prefix + 'bid_count'] += len(cat_df) # Count of all items in this branding category for avg bid calculation

        st.session_state.analysis_data[cat_prefix + 'projected_spend'] += cat_df['Estimated_New_Spend'].sum()
        st.session_state.analysis_data[cat_prefix + 'projected_sales'] += cat_df['Estimated_New_Sales'].sum()
        st.session_state.analysis_data[cat_prefix + 'projected_clicks'] += cat_df['Estimated_New_Clicks'].sum()

    campaign_type_map = {
        'sponsored products': 'sp',
        'sponsored brands': 'sb',
        'sponsored display': 'sd'
    }
    if 'Product' in df.columns:
        for camp_type_full, camp_type_abbr in campaign_type_map.items():
            # Filter for both campaign type and valid rows (Bid > 0.01)
            type_df = df[(df['Product'].astype(str).str.lower() == camp_type_full) & (df['Bid'] > 0.01)]
            st.session_state.analysis_data[camp_type_abbr + '_current_spend'] += type_df['Spend'].sum()
            st.session_state.analysis_data[camp_type_abbr + '_current_sales'] += type_df['Sales'].sum()
            st.session_state.analysis_data[camp_type_abbr + '_current_clicks'] += type_df['Clicks'].sum()
            st.session_state.analysis_data[camp_type_abbr + '_projected_spend'] += type_df['Estimated_New_Spend'].sum()
            st.session_state.analysis_data[camp_type_abbr + '_projected_sales'] += type_df['Estimated_New_Sales'].sum()
            st.session_state.analysis_data[camp_type_abbr + '_projected_clicks'] += type_df['Estimated_New_Clicks'].sum()

    # Calculate bid change distribution
    # For increased bids
    if increased_mask.any():
        percent_increase = ((df['Recommended Bid'] / df['Old Bid']) - 1) * 100
        st.session_state.analysis_data['increased_by_0_10'] += ((percent_increase > 0) & (percent_increase <= 10) & increased_mask).sum()
        st.session_state.analysis_data['increased_by_10_25'] += ((percent_increase > 10) & (percent_increase <= 25) & increased_mask).sum()
        st.session_state.analysis_data['increased_by_25_50'] += ((percent_increase > 25) & (percent_increase <= 50) & increased_mask).sum()
        st.session_state.analysis_data['increased_by_50_plus'] += ((percent_increase > 50) & increased_mask).sum()
    
    # For decreased bids
    if decreased_mask.any():
        percent_decrease = ((df['Old Bid'] / df['Recommended Bid']) - 1) * 100
        st.session_state.analysis_data['decreased_by_0_10'] += ((percent_decrease > 0) & (percent_decrease <= 10) & decreased_mask).sum()
        st.session_state.analysis_data['decreased_by_10_25'] += ((percent_decrease > 10) & (percent_decrease <= 25) & decreased_mask).sum()
        st.session_state.analysis_data['decreased_by_25_50'] += ((percent_decrease > 25) & (percent_decrease <= 50) & decreased_mask).sum()
        st.session_state.analysis_data['decreased_by_50_plus'] += ((percent_decrease > 50) & decreased_mask).sum()

    # --- Top Movers Identification ---
    TOP_N_MOVERS = 10
    df_changed_bids = df[df['Old Bid'] != df['Recommended Bid']].copy() # Consider only rows where bid actually changed
    df_changed_bids['Bid_Change_Abs'] = (df_changed_bids['Recommended Bid'] - df_changed_bids['Old Bid']).abs()
    df_changed_bids['Bid_Change_Pct'] = np.where(
        df_changed_bids['Old Bid'] > 0, 
        ((df_changed_bids['Recommended Bid'] - df_changed_bids['Old Bid']) / df_changed_bids['Old Bid']) * 100,
        np.inf # Represent new bids (old bid was 0) as infinite percent change
    )

    # Determine the best available column for 'Targeting'
    target_col_options = ['Keyword Text', 'Product Targeting Expression', 'Product Targeting ID', 'Ad Group Name']
    target_col = next((col for col in target_col_options if col in df_changed_bids.columns), 'N/A')
    campaign_name_col = camp_col_name if camp_col_name else 'Campaign Name' # Use 'Campaign Name' if informational only is not found
    if campaign_name_col not in df_changed_bids.columns: campaign_name_col = 'N/A' # Fallback for campaign name
    if target_col == 'N/A' and 'Ad Group Name' in df_changed_bids.columns: target_col = 'Ad Group Name' # ensure target_col gets a value if possible

    # Top Increases
    top_increases_df = df_changed_bids[df_changed_bids['Recommended Bid'] > df_changed_bids['Old Bid']].nlargest(TOP_N_MOVERS, 'Bid_Change_Abs')
    for _, row in top_increases_df.iterrows():
        # Calculate ACoS if Sales > 0, otherwise set to 0
        acos = (row['Spend'] / row['Sales'] * 100) if row['Sales'] > 0 else 0
        
        st.session_state.analysis_data['top_bid_increases'].append({
            'campaign': row.get(campaign_name_col, 'N/A'),
            'target': row.get(target_col, 'N/A'),
            'old_bid': row['Old Bid'],
            'new_bid': row['Recommended Bid'],
            'change_pct': row['Bid_Change_Pct'],
            'spend': row.get('Spend', 0),
            'sales': row.get('Sales', 0),
            'acos': acos,
            'current_cpc': row.get('Current_CPC', 0),
            'estimated_new_cpc': row.get('Estimated_New_CPC', 0),
            'vcpm': row.get('VCPM', 0) if row.get('Type') == 'VCPM' else 0
        })
    
    # Top Decreases
    top_decreases_df = df_changed_bids[df_changed_bids['Recommended Bid'] < df_changed_bids['Old Bid']].nlargest(TOP_N_MOVERS, 'Bid_Change_Abs') # largest absolute change
    for _, row in top_decreases_df.iterrows():
        # Calculate ACoS if Sales > 0, otherwise set to 0
        acos = (row['Spend'] / row['Sales'] * 100) if row['Sales'] > 0 else 0
        
        st.session_state.analysis_data['top_bid_decreases'].append({
            'campaign': row.get(campaign_name_col, 'N/A'),
            'target': row.get(target_col, 'N/A'),
            'old_bid': row['Old Bid'],
            'new_bid': row['Recommended Bid'],
            'change_pct': row['Bid_Change_Pct'], # Will be negative
            'spend': row.get('Spend', 0),
            'sales': row.get('Sales', 0),
            'acos': acos,
            'current_cpc': row.get('Current_CPC', 0),
            'estimated_new_cpc': row.get('Estimated_New_CPC', 0),
            'vcpm': row.get('VCPM', 0) if row.get('Type') == 'VCPM' else 0
        })

    # Keyword Projections (This seems to be an existing list, ensure it's populated if needed or remove if redundant)
    # Create a unique identifier for each row (keyword/campaign)
    if 'Keyword' not in df.columns:
        df['Keyword'] = df[camp_col_name] if camp_col_name else df.index
    
    # Ensure all numeric columns are properly converted before calculations
    numeric_columns = ['Clicks', 'Impressions', 'Sales', 'Spend', 'Orders']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    if 'CPC' in df.columns:
        df['CPC'] = pd.to_numeric(df['CPC'], errors='coerce').fillna(0)
    
    # Calculate bid change ratio for each keyword
    df['Bid_Change_Ratio'] = np.where(df['Old Bid'] > 0, df['Recommended Bid'] / df['Old Bid'], 1)
    
    # Estimate new impressions with different elasticity models for increases vs decreases
    mask_increase = df['Bid_Change_Ratio'] > 1.0
    mask_decrease = df['Bid_Change_Ratio'] < 1.0
    mask_no_change = df['Bid_Change_Ratio'] == 1.0
    
    # Apply different elasticity models for impressions
    df['Estimated_Impression_Ratio'] = 1.0  # Default no change
    df.loc[mask_increase, 'Estimated_Impression_Ratio'] = np.power(df.loc[mask_increase, 'Bid_Change_Ratio'], 0.4)  # Lower elasticity for increases
    df.loc[mask_decrease, 'Estimated_Impression_Ratio'] = np.power(df.loc[mask_decrease, 'Bid_Change_Ratio'], 0.6)  # Higher elasticity for decreases
    
    # Estimate new clicks with improved CTR model
    if 'Impressions' in df.columns and 'Clicks' in df.columns and df['Impressions'].sum() > 0:
        # Calculate CTR as a decimal (e.g., 0.03 for 3%)
        df['CTR'] = np.where(df['Impressions'] > 0, df['Clicks'] / df['Impressions'], 0)
        
        # CTR can change slightly with bid changes (higher bids often get better placements)
        df['CTR_Change_Factor'] = np.where(
            mask_increase, 
            1 + (np.power(df['Bid_Change_Ratio'] - 1, 0.5) * 0.1),  # Small increase in CTR for higher bids
            np.where(
                mask_decrease,
                1 - (np.power(1 - df['Bid_Change_Ratio'], 0.5) * 0.05),  # Small decrease in CTR for lower bids
                1.0  # No change
            )
        )
        
        df['Estimated_New_CTR'] = df['CTR'] * df['CTR_Change_Factor']
        df['Estimated_New_Impressions'] = df['Impressions'] * df['Estimated_Impression_Ratio']
        df['Estimated_New_Clicks'] = df['Estimated_New_Impressions'] * df['Estimated_New_CTR']
    else:
        # If impression data not available, use the previously calculated Estimated_New_Clicks
        pass
    
    # Estimate new spend using the improved CPC model from earlier
    # This is already calculated as df['Estimated_New_Spend'] = df['Estimated_New_Clicks'] * df['Estimated_New_CPC']
    
    # Estimate new sales with a more sophisticated model including R-squared correlation
    if 'Sales' in df.columns and 'Clicks' in df.columns and df['Clicks'].sum() > 0:
        # Calculate base conversion metrics
        if 'Orders' in df.columns:
            df['Conversion_Rate'] = np.where(df['Clicks'] > 0, df['Orders'] / df['Clicks'], 0)
            df['AOV'] = np.where(df['Orders'] > 0, df['Sales'] / df['Orders'], 0)
            
            # Apply non-linear model for conversion rate changes
            # Higher bids may improve conversion slightly due to better placements
            df['Conversion_Rate_Factor'] = np.where(
                mask_increase,
                1 + (np.power(df['Bid_Change_Ratio'] - 1, 0.3) * 0.05),  # Small increase for higher bids
                np.where(
                    mask_decrease,
                    1 - (np.power(1 - df['Bid_Change_Ratio'], 0.3) * 0.03),  # Small decrease for lower bids
                    1.0  # No change
                )
            )
            
            df['Estimated_New_Conversion_Rate'] = df['Conversion_Rate'] * df['Conversion_Rate_Factor']
            df['Estimated_New_Orders'] = df['Estimated_New_Clicks'] * df['Estimated_New_Conversion_Rate']
            
            # AOV typically doesn't change much with bid changes
            df['Estimated_New_Sales'] = df['Estimated_New_Orders'] * df['AOV']
        else:
            # If we don't have order data, use a sales-per-click model with diminishing returns
            df['Sales_Per_Click'] = np.where(df['Clicks'] > 0, df['Sales'] / df['Clicks'], 0)
            
            # Apply the previously calculated Sales_Elasticity for a more accurate model
            df['Estimated_New_Sales'] = (df['Estimated_New_Clicks'] * df['Sales_Per_Click'] * 
                                        np.where(df['Sales_Elasticity'].notna(), df['Sales_Elasticity'], 1.0))
    
    # Apply final adjustments to ensure realistic projections
    # Ensure sales don't increase too dramatically for large bid increases
    max_sales_multiplier = 3.0  # Cap sales growth at 3x current sales
    df.loc[df['Sales'] > 0, 'Estimated_New_Sales'] = np.minimum(
        df.loc[df['Sales'] > 0, 'Estimated_New_Sales'],
        df.loc[df['Sales'] > 0, 'Sales'] * max_sales_multiplier
    )
    
    # Calculate projected ACoS with sanity checks
    if df['Estimated_New_Sales'].sum() > 0:
        projected_acos = (df['Estimated_New_Spend'].sum() / df['Estimated_New_Sales'].sum()) * 100
        # Ensure projected ACoS is within reasonable bounds
        if projected_acos > 0 and projected_acos < 200:  # Reasonable ACoS range
            st.session_state.analysis_data['projected_acos'] = projected_acos
        else:
            # Fallback to a more conservative estimate if projection seems unrealistic
            current_acos = (df['Spend'].sum() / df['Sales'].sum()) * 100 if df['Sales'].sum() > 0 else 0
            avg_bid_change = df['Recommended Bid'].sum() / df['Old Bid'].sum() if df['Old Bid'].sum() > 0 else 1.0
            # Adjust current ACoS based on average bid change with diminishing returns
            st.session_state.analysis_data['projected_acos'] = current_acos * np.power(avg_bid_change, 0.7)
    
    # Collect data for ACoS Range Heatmap
    # Only include rows with valid bids (Bid > 0.01) and where bid changes occurred
    valid_bid_change_rows = (df['Bid'] > 0.01) & (df['Old Bid'] != df['Recommended Bid'])
    
    if valid_bid_change_rows.any():
        # Define ACoS ranges
        acos_ranges = [
            (0, 10, '0-10%'),
            (10, 20, '10-20%'),
            (20, 30, '20-30%'),
            (30, 40, '30-40%'),
            (40, 50, '40-50%'),
            (50, 75, '50-75%'),
            (75, 100, '75-100%'),
            (100, float('inf'), '100%+'),
        ]
        
        # Define spend ranges
        spend_ranges = [
            (0, 10, '$0-10'),
            (10, 50, '$10-50'),
            (50, 100, '$50-100'),
            (100, 250, '$100-250'),
            (250, 500, '$250-500'),
            (500, 1000, '$500-1000'),
            (1000, float('inf'), '$1000+'),
        ]
        
        # Calculate ACoS for each row
        df['Current_ACoS'] = np.where(df['Sales'] > 0, (df['Spend'] / df['Sales']) * 100, 0)
        
        # Process each valid row for the heatmap
        for _, row in df[valid_bid_change_rows].iterrows():
            # Determine ACoS range
            acos_range = 'Unknown'
            for min_acos, max_acos, range_label in acos_ranges:
                if min_acos <= row['Current_ACoS'] < max_acos:
                    acos_range = range_label
                    break
            
            # Determine spend range
            spend_range = 'Unknown'
            for min_spend, max_spend, range_label in spend_ranges:
                if min_spend <= row['Spend'] < max_spend:
                    spend_range = range_label
                    break
            
            # Add to heatmap data
            st.session_state.analysis_data['acos_heatmap_data'].append({
                'acos_range': acos_range,
                'spend_range': spend_range,
                'count': 1,
                'bid_change': row['Recommended Bid'] - row['Old Bid']
            })
    
    # Store projections in session state
    if 'keyword_projections' not in st.session_state:
        st.session_state.keyword_projections = []
    
    # Extract relevant columns for projections
    projection_columns = ['Keyword', 'Spend', 'Sales', 'Clicks', 'Impressions', 'Estimated_New_Spend', 'Estimated_New_Sales', 'Estimated_New_Clicks', 'Estimated_New_Impressions']
    projections_df = df[[col for col in projection_columns if col in df.columns]].copy()
    st.session_state.keyword_projections.append(projections_df)
    
    # Replace NaN with empty strings for cleaner output
    df = df.replace({np.nan: ''})
    
    return df

def save_preset(filename, filters, filter_groups, target_acos, increase_percent, decrease_percent, adjust_based_on_increase, adjust_based_on_decrease, min_spend_threshold):
    preset_data = {
        "filters": filters,
        "filter_groups": filter_groups,
        "target_acos": target_acos,
        "increase_percent": increase_percent,
        "decrease_percent": decrease_percent,
        "adjust_based_on_increase": adjust_based_on_increase,
        "adjust_based_on_decrease": adjust_based_on_decrease,
        "min_spend_threshold": min_spend_threshold
    }
    with open(filename, 'w') as f:
        json.dump(preset_data, f, indent=4)

def load_preset(filename):
    with open(filename, 'r') as f:
        return json.load(f)

# --- Sidebar: Preset Save/Load ---
st.sidebar.header("Presets")
preset_action = st.sidebar.radio("Preset Actions", ["None", "Save Preset", "Load Preset"])
if preset_action == "Save Preset":
    preset_filename = st.sidebar.text_input("Preset filename", "preset.json")
    if st.sidebar.button("Save Preset"):
        save_preset(
            preset_filename,
            st.session_state.filters,
            st.session_state.filter_groups,
            st.session_state.get("target_acos", ""),
            st.session_state.get("increase_percent", ""),
            st.session_state.get("decrease_percent", ""),
            st.session_state.get("adjust_based_on_increase", ""),
            st.session_state.get("adjust_based_on_decrease", ""),
            st.session_state.min_spend_threshold
        )
        st.sidebar.success("Preset saved!")
elif preset_action == "Load Preset":
    preset_file = st.sidebar.file_uploader("Upload Preset JSON", type=["json"], key="preset_upload")
    if preset_file:
        preset_data = json.load(preset_file)
        st.session_state.filters = preset_data.get("filters", [])
        st.session_state.filter_groups = preset_data.get("filter_groups", [])
        st.session_state.target_acos = preset_data.get("target_acos", "")
        st.session_state.increase_percent = preset_data.get("increase_percent", "")
        st.session_state.decrease_percent = preset_data.get("decrease_percent", "")
        st.session_state.adjust_based_on_increase = preset_data.get("adjust_based_on_increase", "")
        st.session_state.adjust_based_on_decrease = preset_data.get("adjust_based_on_decrease", "")
        st.session_state.min_spend_threshold = preset_data.get("min_spend_threshold", None)
        st.sidebar.success("Preset loaded!")

# --- Main UI ---
tabs = st.tabs(["Optimizer", "Analysis"])

with tabs[0]:
    st.header("Bulk File Upload")
    uploaded_file = st.file_uploader("Upload Bulk Excel File", type=["xlsx"], key="bulk_file")
    if uploaded_file:
        st.session_state.uploaded_file_name = uploaded_file.name
        st.session_state.df_dict = pd.read_excel(uploaded_file, sheet_name=None)
        for df in st.session_state.df_dict.values():
            df.columns = df.columns.str.strip()
        st.success(f"Uploaded: {uploaded_file.name}")

    # st.header("Optimizer Settings") # Now part of the expander
    with st.expander("Optimizer Settings", expanded=True): # Keep it expanded by default initially
        col1, col2, col3 = st.columns(3)
        with col1:
            target_acos = st.text_input("Default Target ACoS (%)", value=st.session_state.target_acos, key="target_acos_input") # Changed key to avoid conflict if st.session_state.target_acos is used directly elsewhere
            st.session_state.target_acos = target_acos # Ensure session state is updated
        with col2:
            increase_percent = st.text_input("Limit increases to (%)", value=st.session_state.increase_percent, key="increase_percent_input")
            st.session_state.increase_percent = increase_percent
        with col3:
            decrease_percent = st.text_input("Limit decreases to (%)", value=st.session_state.decrease_percent, key="decrease_percent_input")
            st.session_state.decrease_percent = decrease_percent
        
        col4, col5 = st.columns(2)
        with col4:
            adjust_based_on_increase = st.selectbox("Increase per unit of", ["Clicks", "Spend", "Orders"], 
                                                    index=["Clicks", "Spend", "Orders"].index(st.session_state.adjust_based_on_increase), 
                                                    key="adjust_based_on_increase_input")
            st.session_state.adjust_based_on_increase = adjust_based_on_increase
        with col5:
            adjust_based_on_decrease = st.selectbox("Decrease per unit of", ["Clicks", "Spend", "Orders"], 
                                                    index=["Clicks", "Spend", "Orders"].index(st.session_state.adjust_based_on_decrease), 
                                                    key="adjust_based_on_decrease_input")
            st.session_state.adjust_based_on_decrease = adjust_based_on_decrease
        
        min_spend = st.text_input("Minimum Spend Threshold", value=st.session_state.min_spend_threshold, key="min_spend_input")
        st.session_state.min_spend_threshold = min_spend

    # --- Filters ---
    st.subheader("Step 1: Add Filter Conditions")
    
    # Input for adding a new filter condition
    filter_columns = ["Campaign Name", "Product", "State", "Bid", "Clicks", "Sales", "Orders", "ACoS", "Spend"]
    filter_types = ["equals", "contains", "greater than", "less than", "doesn't contain", "doesn't equal", "less than or equal to", "greater than or equal to"]
    
    with st.form("add_filter_form"):
        st.markdown("Define a condition to add to the filter group:")
        colf1, colf2, colf3, colf4 = st.columns([1,1,1,1])
        filter_column = colf1.selectbox("Column", filter_columns, key="filter_column")
        filter_type = colf2.selectbox("Type", filter_types, key="filter_type")
        filter_value = colf3.text_input("Value", key="filter_value")
        filter_logic = colf4.selectbox("Logic", ["AND", "OR"], key="filter_logic")
        
        add_filter_btn = st.form_submit_button("Add Condition", use_container_width=True)

        if add_filter_btn:
            if not all([filter_column, filter_type, filter_value if filter_value != "" else True]):
                st.error("Please fill all filter fields!")
            else:
                # Create new condition with selected logic
                new_condition = {
                    "column": filter_column,
                    "type": filter_type,
                    "value": filter_value,
                    "logic": filter_logic
                }
                
                # First condition in a group doesn't need logic specified
                if not st.session_state.filters:
                    new_condition["logic"] = "FIRST"
                
                st.session_state.filters.append(new_condition)
                st.success(f"Added: {filter_column} {filter_type} {filter_value} with {filter_logic} logic")
                st.rerun()

    # Step 2: Visual filter group builder
    st.subheader("Step 2: Build Filter Groups")
    
    # Create a visual representation of existing filter groups
    if st.session_state.filter_groups:
        st.markdown("#### Existing Filter Groups")
        
        # Display a visual OR separator between groups
        for i, group_data in enumerate(st.session_state.filter_groups):
            group_filters, group_acos_val = group_data
            
            # Create a container with a border for each group
            with st.container():
                # Group header with ACoS
                st.markdown(f"""
                <div style='background-color: #2c3e50; color: white; padding: 10px; border-radius: 5px 5px 0 0;'>
                <div style='display: flex; justify-content: space-between;'>
                <div>Group {i+1}</div>
                <div>Target ACoS: {group_acos_val*100:.2f}%</div>
                </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Group body with filter conditions
                with st.container():
                    st.markdown("""
                    <div style='background-color: #f8f9fa; padding: 10px; border: 1px solid #dee2e6; border-radius: 0 0 5px 5px;'>
                    <div style='margin-bottom: 8px; color: #666;'><b>AND</b> logic - all conditions must match</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # List all filter conditions in this group
                    for f_idx, filter_item in enumerate(group_filters):
                        cols = st.columns([0.9, 0.1])
                        
                        # Handle both old and new filter formats
                        if isinstance(filter_item, dict):  # New format
                            f_col = filter_item["column"]
                            f_type = filter_item["type"]
                            f_val = filter_item["value"]
                        else:  # Old format (tuple)
                            f_col, f_type, f_val = filter_item
                            
                        cols[0].markdown(f"**{f_col}** {f_type} _`{f_val}`_")
                        if cols[1].button("❌", key=f"remove_filter_group{i}_filter{f_idx}"):
                            st.session_state.filter_groups[i][0].pop(f_idx)
                            if not st.session_state.filter_groups[i][0]:
                                # st.warning(f"Group {i+1} is now empty. Consider deleting it.")  # Removed as per user request
                                pass
                            st.rerun()
                    
                    # Group actions
                    col1, col2 = st.columns(2)
                    with col1:
                        new_acos = st.text_input(f"Update ACoS (%)", value=f"{group_acos_val*100:.2f}", key=f"update_acos_{i}")
                    with col2:
                        if st.button(f"Update ACoS", key=f"update_btn_{i}"):
                            try:
                                updated_acos_val = float(new_acos) / 100
                                st.session_state.filter_groups[i] = (group_filters, updated_acos_val)
                                st.success(f"Updated to {updated_acos_val*100:.2f}%")
                                st.rerun()
                            except ValueError:
                                st.error("Enter a valid number")
                    
                    if st.button(f"Delete Group", key=f"delete_group_{i}", type="secondary"):
                        st.session_state.filter_groups.pop(i)
                        st.session_state.filters.pop(i)
                        st.success(f"Group {i+1} removed.")
                        st.rerun()
            
            # Add OR separator between groups (except after the last one)
            if i < len(st.session_state.filter_groups) - 1:
                st.markdown("""
                <div style='display: flex; justify-content: center; margin: 15px 0;'>
                <div style='background-color: #ffc107; color: black; padding: 8px 30px; border-radius: 20px; font-weight: bold; font-size: 1.2em;'>OR</div>
                </div>
                """, unsafe_allow_html=True)


    # Current group builder section
    
    # Create a styled container for the current filter group
    with st.container():
        # Display current building filters
        current_building_filters = st.session_state.filters
        
        # Show current conditions
        if current_building_filters:
            st.markdown("""
            <div style='background-color: #343a40; color: white; padding: 10px; border-radius: 5px 5px 0 0;'>
            <div>Current Filter Group</div>
            </div>
            """, unsafe_allow_html=True)
            
            # List all current filter conditions with their logic
            for f_idx, condition in enumerate(current_building_filters):
                cols_new = st.columns([0.2, 0.7, 0.1])
                
                # Display logic type (except for first condition)
                if condition["logic"] != "FIRST":
                    logic_color = "#28a745" if condition["logic"] == "AND" else "#dc3545"
                    cols_new[0].markdown(f"<div style='font-weight: bold; color: {logic_color};'>{condition['logic']}</div>", unsafe_allow_html=True)
                else:
                    cols_new[0].write("")
                    
                cols_new[1].markdown(f"**{condition['column']}** {condition['type']} _`{condition['value']}`_")
                if cols_new[2].button("❌", key=f"remove_current_filter_{f_idx}"):
                    st.session_state.filters.pop(f_idx)
                    # If we removed the first item, update the next one to be FIRST
                    if f_idx == 0 and len(st.session_state.filters) > 0:
                        st.session_state.filters[0]["logic"] = "FIRST"
                    st.rerun()
            
            # Clear button
            if st.button("Clear All Conditions", key="clear_current_filters", type="secondary"):
                st.session_state.filters = []
                st.rerun()
        else:
            st.info("No conditions added yet. Use Step 1 above to add filter conditions.")
        
        # Form to set ACoS and finalize the group
        if current_building_filters:
            with st.form("set_new_group_acos_form"):
                st.markdown("### Finalize This Filter Group")
                new_group_acos_str = st.text_input("Set Target ACoS for this group (%)", key="new_group_acos", help="Enter as a percentage, e.g., 30 for 30%")
                if st.form_submit_button("Finalize Group and Start New One", use_container_width=True):
                    if not current_building_filters:
                        st.error("Cannot finalize an empty group. Add at least one filter condition first.")
                    else:
                        try:
                            new_group_acos_val = float(new_group_acos_str) / 100
                            # Save the current filters as a finalized group
                            st.session_state.filter_groups.append((list(current_building_filters), new_group_acos_val))
                            # Clear current filters for a new group
                            st.session_state.filters = []
                            st.success(f"Group finalized with Target ACoS: {new_group_acos_val*100:.2f}%")
                            st.rerun()
                        except ValueError:
                            st.error("Please enter a valid numeric ACoS value.")

    # Global filter management actions
    if st.session_state.filter_groups:
        st.markdown("---")
        col_manage1, col_manage2 = st.columns(2)
        
        with col_manage1:
            if st.button("Remove Last Group", key="remove_last_finalized_group", use_container_width=True):
                if st.session_state.filter_groups:
                    st.session_state.filter_groups.pop()
                    if len(st.session_state.filters) > 1:
                        st.session_state.filters.pop(-2)
                    st.success("Last group removed.")
                    st.rerun()
                else:
                    # st.warning("No groups to remove.")  # Removed as per user request
                    pass
        
        with col_manage2:
            if st.button("Clear All Groups", key="clear_all_filters", type="secondary", use_container_width=True):
                st.session_state.filters = [[]]
                st.session_state.filter_groups = []
                st.success("All filter groups cleared.")
                st.rerun()

    # --- Process Bulk File ---
    st.header("Process Bulk File")
    if st.button("Process Bulk File"):
        if not st.session_state.df_dict:
            st.error("Please upload a bulk file first.")
        else:
            try:
                default_target_acos = float(st.session_state.target_acos) / 100
                increase_percent = float(st.session_state.increase_percent) / 100
                decrease_percent = float(st.session_state.decrease_percent) / 100
                adjust_based_on_increase = st.session_state.adjust_based_on_increase
                adjust_based_on_decrease = st.session_state.adjust_based_on_decrease
                min_spend_threshold = float(st.session_state.min_spend_threshold) if st.session_state.min_spend_threshold else None

                # Reset analysis data for new processing
                st.session_state.analysis_data = {
                    'increased': 0,
                    'decreased': 0,
                    'unchanged': 0,
                    'total_rows': 0,
                    'total_increase_amount': 0,  # Sum of positive bid changes
                    'total_decrease_amount': 0,  # Sum of absolute negative bid changes
                    'sp_count': 0,
                    'sb_count': 0,
                    'sd_count': 0,
                    'vcpm_count': 0,
                    'total_spend': 0,
                    'total_sales': 0,
                    'total_clicks': 0,
                    'total_impressions': 0,
                    'increased_by_0_10': 0,
                    'increased_by_10_25': 0,
                    'increased_by_25_50': 0,
                    'increased_by_50_plus': 0,
                    'decreased_by_0_10': 0,
                    'decreased_by_10_25': 0,
                    'decreased_by_25_50': 0,
                    'decreased_by_50_plus': 0,
                    'avg_old_bid': 0, # Will store sum of old bids; average calculated in UI
                    'avg_new_bid': 0, # Will store sum of new bids; average calculated in UI
                    'current_acos': 0, # Overall, calculated as total_spend / total_sales in UI
                    'projected_acos': 0, # Overall, calculated as projected_total_spend / projected_total_sales in UI

                    # New Overall Projections
                    'projected_total_spend': 0,
                    'projected_total_sales': 0,
                    'projected_total_clicks': 0,

                    # New Branding Metrics
                    'branded_total_rows': 0, 'non_branded_total_rows': 0, 'unknown_total_rows': 0,
                    'branded_increased_bids': 0, 'non_branded_increased_bids': 0, 'unknown_increased_bids': 0,
                    'branded_decreased_bids': 0, 'non_branded_decreased_bids': 0, 'unknown_decreased_bids': 0,
                    'branded_unchanged_bids': 0, 'non_branded_unchanged_bids': 0, 'unknown_unchanged_bids': 0,

                    'branded_current_spend': 0, 'non_branded_current_spend': 0, 'unknown_current_spend': 0,
                    'branded_current_sales': 0, 'non_branded_current_sales': 0, 'unknown_current_sales': 0,
                    'branded_current_clicks': 0, 'non_branded_current_clicks': 0, 'unknown_current_clicks': 0,
                    # ACoS for branded categories will be calculated in the UI

                    'branded_projected_spend': 0, 'non_branded_projected_spend': 0, 'unknown_projected_spend': 0,
                    'branded_projected_sales': 0, 'non_branded_projected_sales': 0, 'unknown_projected_sales': 0,
                    'branded_projected_clicks': 0, 'non_branded_projected_clicks': 0, 'unknown_projected_clicks': 0,
                    # Projected ACoS for branded categories will be calculated in the UI
            
                    'branded_sum_old_bids': 0, 'non_branded_sum_old_bids': 0, 'unknown_sum_old_bids': 0,
                    'branded_sum_new_bids': 0, 'non_branded_sum_new_bids': 0, 'unknown_sum_new_bids': 0,
                    'branded_bid_count': 0, 'non_branded_bid_count': 0, 'unknown_bid_count': 0, # For calculating avg bids per brand type

                    # New Campaign Type Metrics (beyond just counts)
                    'sp_current_spend': 0, 'sb_current_spend': 0, 'sd_current_spend': 0,
                    'sp_current_sales': 0, 'sb_current_sales': 0, 'sd_current_sales': 0,
                    'sp_current_clicks': 0, 'sb_current_clicks': 0, 'sd_current_clicks': 0,
                    # Current ACoS for campaign types will be calculated in the UI

                    'sp_projected_spend': 0, 'sb_projected_spend': 0, 'sd_projected_spend': 0,
                    'sp_projected_sales': 0, 'sb_projected_sales': 0, 'sd_projected_sales': 0,
                    'sp_projected_clicks': 0, 'sb_projected_clicks': 0, 'sd_projected_clicks': 0,
                    # Projected ACoS for campaign types will be calculated in the UI

                    # Top Movers (holding up to N items, e.g., 10)
                    'top_bid_increases': [], 
                    'top_bid_decreases': [],
                    
                    # ACoS Range Heatmap Data
                    'acos_heatmap_data': []
                }
                st.session_state.keyword_projections = []
                
                # --- Sheet selection logic ---
                all_sheets = dict(st.session_state.df_dict)
                # If both 'SB Multi Ad Group Campaigns' and 'Sponsored Brands Campaigns' exist, skip 'Sponsored Brands Campaigns'
                sheet_names = list(all_sheets.keys())
                if 'SB Multi Ad Group Campaigns' in sheet_names and 'Sponsored Brands Campaigns' in sheet_names:
                    all_sheets.pop('Sponsored Brands Campaigns', None)

                processed_sheets = {}
                eligible_found = False
                for sheet_name, df in all_sheets.items():
                    df = df.copy()
                    df.columns = df.columns.str.strip()

                    # Ensure 'Operation' column exists before any further processing for this sheet
                    if 'Product' not in df.columns:
                        continue
                    # Only process if any row has Product as one of the three types
                    prod_types = ["Sponsored Brands", "Sponsored Products", "Sponsored Display"]
                    if not df['Product'].astype(str).str.strip().isin(prod_types).any():
                        continue
                    eligible_found = True
                    processed = process_sheet(
                        df,
                        default_target_acos,
                        increase_percent,
                        decrease_percent,
                        adjust_based_on_increase,
                        adjust_based_on_decrease,
                        st.session_state.filter_groups,
                        min_spend_threshold
                    )
                    # Only keep rows where Product is in the allowed types
                    allowed_types = ["Sponsored Brands", "Sponsored Products", "Sponsored Display"]
                    processed = processed[processed['Product'].astype(str).str.strip().isin(allowed_types)]
                    processed_sheets[sheet_name] = processed
                if not eligible_found:
                    # st.warning("No eligible sheets found with 'Product' as 'Sponsored Brands', 'Sponsored Products', or 'Sponsored Display'.")  # Removed as per user request
                    pass
                else:
                    st.session_state.processed_sheets = processed_sheets
                    st.success("Bulk file processed!")
            except Exception as e:
                st.error(f"Error processing file: {e}")
    # Download processed file
    if "processed_sheets" in st.session_state:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for sheet_name, df_from_session in st.session_state.processed_sheets.items(): # Iterate over a copy from session state
                if 'Operation' in df_from_session.columns: # Process only if 'Operation' column exists
                    df = df_from_session.copy() # Work on a copy to avoid modifying session state

                    # Convert ID columns to nullable integer type to remove decimals and handle NaNs
                    if 'Product Targeting ID' in df.columns:
                        df['Product Targeting ID'] = pd.to_numeric(df['Product Targeting ID'], errors='coerce').astype('Int64')
                    if 'Keyword ID' in df.columns:
                        df['Keyword ID'] = pd.to_numeric(df['Keyword ID'], errors='coerce').astype('Int64')

                    df = remove_hyperlinks_from_df(df) # remove_hyperlinks_from_df modifies df
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                # else: sheets without 'Operation' column are skipped from export (existing behavior)
        output.seek(0)
        st.download_button(
            label="Download Processed File",
            data=output,
            file_name="processed_bulk_file.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

with tabs[1]:
    st.header("Analysis Dashboard")
    if "processed_sheets" not in st.session_state:
        st.info("No data processed yet. Please process a file in the Optimizer tab.")
    else:
        # Overall Summary
        st.subheader("Optimization Summary")
        
        # Retrieve necessary values from session state first for clarity
        analysis_data = st.session_state.analysis_data
        total_rows = analysis_data.get('total_rows', 0)
        
        current_total_spend = analysis_data.get('total_spend', 0)
        current_total_sales = analysis_data.get('total_sales', 0)
        current_total_clicks = analysis_data.get('total_clicks', 0)
        
        projected_total_spend = analysis_data.get('projected_total_spend', 0)
        projected_total_sales = analysis_data.get('projected_total_sales', 0)
        projected_total_clicks = analysis_data.get('projected_total_clicks', 0)
        
        avg_old_bid_sum = analysis_data.get('avg_old_bid', 0) # This is actually sum of old bids
        avg_new_bid_sum = analysis_data.get('avg_new_bid', 0) # This is actually sum of new bids
        
        with st.container():
            st.markdown("""<hr style="height:1px;border:none;color:#333;background-color:#333;" />""", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Keywords/Targets", format_number(total_rows))
                st.metric("Bids Increased", format_number(analysis_data.get('increased', 0)))
                st.metric("Bids Decreased", format_number(analysis_data.get('decreased', 0)))
                st.metric("Bids Unchanged", format_number(analysis_data.get('unchanged', 0)))
            
            with col2:
                # ACoS Calculations
                current_acos_val = (current_total_spend / current_total_sales) * 100 if current_total_sales > 0 else 0
                st.metric("Current ACoS", f"{current_acos_val:.2f}%")
                projected_acos_val = (projected_total_spend / projected_total_sales) * 100 if projected_total_sales > 0 else 0
                st.metric("Projected ACoS", f"{projected_acos_val:.2f}%")
                acos_change = projected_acos_val - current_acos_val
                st.metric("ACoS Change", f"{acos_change:.2f}%", delta=f"{acos_change:.2f}%", delta_color="inverse") # Lower ACoS is better
                
                # RoAS Calculations
                current_roas_val = current_total_sales / current_total_spend if current_total_spend > 0 else 0
                st.metric("Current RoAS", f"{current_roas_val:.2f}x")
                projected_roas_val = projected_total_sales / projected_total_spend if projected_total_spend > 0 else 0
                st.metric("Projected RoAS", f"{projected_roas_val:.2f}x")
                roas_change = projected_roas_val - current_roas_val
                st.metric("RoAS Change", f"{roas_change:.2f}x", delta=f"{roas_change:.2f}x") # Higher RoAS is better
            
            with col3:
                # Average Bid Calculations
                avg_old_bid = avg_old_bid_sum / total_rows if total_rows > 0 else 0
                avg_new_bid = avg_new_bid_sum / total_rows if total_rows > 0 else 0
                st.metric("Avg Old Bid", format_currency(avg_old_bid))
                st.metric("Avg New Bid", format_currency(avg_new_bid))
                bid_change_pct = ((avg_new_bid / avg_old_bid) - 1) * 100 if avg_old_bid > 0 else 0
                st.metric("Avg Bid Change", f"{bid_change_pct:.2f}%")
                
                # CPC Calculations
                current_cpc_val = current_total_spend / current_total_clicks if current_total_clicks > 0 else 0
                st.metric("Current CPC", format_currency(current_cpc_val))
                projected_cpc_val = projected_total_spend / projected_total_clicks if projected_total_clicks > 0 else 0
                st.metric("Projected CPC", format_currency(projected_cpc_val))
                cpc_change = projected_cpc_val - current_cpc_val
                st.metric("CPC Change", format_currency(cpc_change), delta=f"{cpc_change:+.2f}", delta_color="inverse") # Lower CPC is better
            st.markdown("""<hr style="height:1px;border:none;color:#333;background-color:#333;" />""", unsafe_allow_html=True)
        
        # No Projected Performance Impact section as requested
        st.markdown("""<hr style="height:1px;border:none;color:#333;background-color:#333;" />""", unsafe_allow_html=True)
        
        # Bid Change Distribution
        st.subheader("Bid Change Distribution")
        with st.container():
            col_increases, col_decreases = st.columns(2)
            
            with col_increases:
                st.markdown("**Bid Increases**")
                st.metric("Increased by 0-10%", format_number(analysis_data.get('increased_by_0_10', 0)))
                st.metric("Increased by 10-25%", format_number(analysis_data.get('increased_by_10_25', 0)))
                st.metric("Increased by 25-50%", format_number(analysis_data.get('increased_by_25_50', 0)))
                st.metric("Increased by 50%+", format_number(analysis_data.get('increased_by_50_plus', 0)))
            
            with col_decreases:
                st.markdown("**Bid Decreases**")
                st.metric("Decreased by 0-10%", format_number(analysis_data.get('decreased_by_0_10', 0)))
                st.metric("Decreased by 10-25%", format_number(analysis_data.get('decreased_by_10_25', 0)))
                st.metric("Decreased by 25-50%", format_number(analysis_data.get('decreased_by_25_50', 0)))
                st.metric("Decreased by 50%+", format_number(analysis_data.get('decreased_by_50_plus', 0)))
            
            # Add a distribution chart for bid changes
            st.subheader("Bid Change Distribution Chart")
            
            # Create data for the distribution chart
            bid_change_data = {
                "Category": [
                    "Increased 0-10%", "Increased 10-25%", "Increased 25-50%", "Increased 50%+",
                    "Decreased 0-10%", "Decreased 10-25%", "Decreased 25-50%", "Decreased 50%+"
                ],
                "Count": [
                    analysis_data.get('increased_by_0_10', 0),
                    analysis_data.get('increased_by_10_25', 0),
                    analysis_data.get('increased_by_25_50', 0),
                    analysis_data.get('increased_by_50_plus', 0),
                    analysis_data.get('decreased_by_0_10', 0),
                    analysis_data.get('decreased_by_10_25', 0),
                    analysis_data.get('decreased_by_25_50', 0),
                    analysis_data.get('decreased_by_50_plus', 0)
                ],
                "Type": [
                    "Increase", "Increase", "Increase", "Increase",
                    "Decrease", "Decrease", "Decrease", "Decrease"
                ]
            }
            
            bid_change_df = pd.DataFrame(bid_change_data)
            if not bid_change_df['Count'].sum() == 0:
                # Create a bar chart
                chart = alt.Chart(bid_change_df).mark_bar().encode(
                    x=alt.X('Category:N', sort=None),  # Keep the original order
                    y='Count:Q',
                    color=alt.Color('Type:N', scale=alt.Scale(
                        domain=['Increase', 'Decrease'],
                        range=['#28a745', '#dc3545']
                    ))
                ).properties(
                    height=300
                )
                
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No bid change data available for chart.")
            
            # Add ACoS Range Heatmap
            st.subheader("ACoS Range Heatmap")
            
            # Create sample data if no real data exists yet
            # This helps with debugging and ensures the visualization code works
            if 'acos_heatmap_data' not in st.session_state.analysis_data or len(st.session_state.analysis_data['acos_heatmap_data']) == 0:
                # For debugging only - create some sample data
                if st.checkbox("Show sample heatmap data for debugging"):
                    sample_data = []
                    acos_ranges = ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50-75%', '75-100%', '100%+'] 
                    spend_ranges = ['$0-10', '$10-50', '$50-100', '$100-250', '$250-500', '$500-1000', '$1000+']
                    
                    # Generate some sample data
                    for acos in acos_ranges:
                        for spend in spend_ranges:
                            # Create more data points in the middle ranges
                            if acos in ['20-30%', '30-40%'] and spend in ['$50-100', '$100-250']:
                                count = np.random.randint(10, 30)
                            else:
                                count = np.random.randint(0, 10)
                                
                            sample_data.append({
                                'acos_range': acos,
                                'spend_range': spend,
                                'count': count
                            })
                    
                    # Use the sample data
                    heatmap_df = pd.DataFrame(sample_data)
                    st.success("Using sample data for demonstration purposes.")
                else:
                    st.info("No ACoS range data available for heatmap. Process a file to generate this visualization.")
                    heatmap_df = pd.DataFrame()  # Create empty DataFrame to skip visualization
            else:
                # Use the real data
                heatmap_df = pd.DataFrame(st.session_state.analysis_data['acos_heatmap_data'])
            
            # Ensure we have data to display
            if len(heatmap_df) > 0:
                try:
                    # Create a pivot table for the heatmap
                    pivot_df = heatmap_df.pivot_table(
                        index='spend_range', 
                        columns='acos_range', 
                        values='count', 
                        aggfunc='sum',
                        fill_value=0
                    )
                    
                    # Define the order for spend ranges
                    spend_order = ['$0-10', '$10-50', '$50-100', '$100-250', '$250-500', '$500-1000', '$1000+']
                    
                    # Define the order for ACoS ranges
                    acos_order = ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50-75%', '75-100%', '100%+']
                    
                    # Create a heatmap using Altair
                    # First melt the pivot table back to long form
                    heatmap_data = pivot_df.reset_index().melt(
                        id_vars=['spend_range'],
                        var_name='acos_range',
                        value_name='count'
                    )
                    
                    # Create the heatmap
                    heatmap = alt.Chart(heatmap_data).mark_rect().encode(
                        x=alt.X('acos_range:N', title='ACoS Range (%)', 
                              sort=acos_order if all(r in acos_order for r in heatmap_data['acos_range'].unique()) else None),
                        y=alt.Y('spend_range:N', title='Spend Range ($)', 
                              sort=spend_order if all(r in spend_order for r in heatmap_data['spend_range'].unique()) else None),
                        color=alt.Color('count:Q', scale=alt.Scale(scheme='viridis')),
                        tooltip=['spend_range', 'acos_range', 'count']
                    ).properties(
                        title='Bid Changes by ACoS and Spend Ranges',
                        width='container',
                        height=300
                    )
                    
                    # Add text labels for the counts
                    max_count = heatmap_data['count'].max() if len(heatmap_data) > 0 else 1
                    text = alt.Chart(heatmap_data).mark_text(baseline='middle').encode(
                        x=alt.X('acos_range:N', sort=acos_order if all(r in acos_order for r in heatmap_data['acos_range'].unique()) else None),
                        y=alt.Y('spend_range:N', sort=spend_order if all(r in spend_order for r in heatmap_data['spend_range'].unique()) else None),
                        text=alt.Text('count:Q'),
                        color=alt.condition(
                            alt.datum.count > max_count / 2,
                            alt.value('white'),
                            alt.value('black')
                        )
                    )
                    
                    # Combine the heatmap and text
                    final_chart = heatmap + text
                    st.altair_chart(final_chart, use_container_width=True)
                except Exception as e:
                    st.error(f"Error creating heatmap: {e}")
                    st.write("Heatmap data preview:")
                    st.write(heatmap_df.head())
            else:
                st.info("No ACoS range data available for heatmap. Process a file to generate this visualization.")
            
            st.markdown("""<hr style="height:1px;border:none;color:#333;background-color:#333;" />""", unsafe_allow_html=True)
        
        # Campaign Type Breakdown
        st.subheader("Campaign Type Breakdown")
        sp_count = analysis_data.get('sp_count', 0)
        sb_count = analysis_data.get('sb_count', 0)
        sd_count = analysis_data.get('sd_count', 0)
        vcpm_count = analysis_data.get('vcpm_count', 0)
        
        col_sp, col_sb, col_sd, col_vcpm = st.columns(4)
        with col_sp:
            st.metric("Sponsored Products", format_number(sp_count))
        with col_sb:
            st.metric("Sponsored Brands", format_number(sb_count))
        with col_sd:
            st.metric("Sponsored Display", format_number(sd_count))
        with col_vcpm:
            st.metric("VCPM Campaigns", format_number(vcpm_count))
        
        campaign_types_data = {
            "Sponsored Products": sp_count,
            "Sponsored Brands": sb_count,
            "Sponsored Display": sd_count,
            "VCPM Campaigns": vcpm_count
        }
        
        # Filter out campaign types with zero count for a cleaner chart
        chart_data = {k: v for k, v in campaign_types_data.items() if v > 0}
        if chart_data:
            campaign_df = pd.DataFrame({
                'Campaign Type': list(chart_data.keys()),
                'Count': list(chart_data.values())
            })
            st.bar_chart(campaign_df.set_index('Campaign Type'))
        else:
            st.text("No campaign data available for chart.")
        st.markdown("""<hr style="height:1px;border:none;color:#333;background-color:#333;" />""", unsafe_allow_html=True)
        
        # Top Changed Targets
        st.subheader("Top Changed Targets")
        
        # Create tabs for increases and decreases
        top_targets_tabs = st.tabs(["Top Bid Increases", "Top Bid Decreases"])
        
        # Check if we have data
        has_increase_data = len(st.session_state.analysis_data.get('top_bid_increases', [])) > 0
        has_decrease_data = len(st.session_state.analysis_data.get('top_bid_decreases', [])) > 0
        
        # Tab for top bid increases
        with top_targets_tabs[0]:
            if has_increase_data:
                # Create a DataFrame for top increases
                top_increases = st.session_state.analysis_data['top_bid_increases']
                increases_df = pd.DataFrame(top_increases)
                
                # Format the data for display
                increases_df['old_bid'] = increases_df['old_bid'].apply(lambda x: f"${x:.2f}")
                increases_df['new_bid'] = increases_df['new_bid'].apply(lambda x: f"${x:.2f}")
                increases_df['change_pct'] = increases_df['change_pct'].apply(lambda x: f"+{x:.1f}%")
                increases_df['spend'] = increases_df['spend'].apply(lambda x: f"${x:.2f}")
                increases_df['sales'] = increases_df['sales'].apply(lambda x: f"${x:.2f}")
                increases_df['acos'] = increases_df['acos'].apply(lambda x: f"{x:.2f}%")
                increases_df['current_cpc'] = increases_df['current_cpc'].apply(lambda x: f"${x:.2f}")
                increases_df['estimated_new_cpc'] = increases_df['estimated_new_cpc'].apply(lambda x: f"${x:.2f}")
                increases_df['vcpm'] = increases_df['vcpm'].apply(lambda x: f"${x:.2f}" if x > 0 else "N/A")
                
                # Rename columns for display
                increases_df.columns = ['Campaign', 'Target', 'Old Bid', 'New Bid', 'Change %', 'Spend', 'Sales', 'ACoS', 'Current CPC', 'Projected CPC', 'VCPM']
                
                # Display the table with styling
                st.markdown("### Top Bid Increases")
                st.markdown("These targets received the largest bid increases:")
                st.dataframe(
                    increases_df,
                    column_config={
                        "Campaign": st.column_config.TextColumn("Campaign"),
                        "Target": st.column_config.TextColumn("Target", width="large"),
                        "Old Bid": st.column_config.TextColumn("Old Bid"),
                        "New Bid": st.column_config.TextColumn("New Bid"),
                        "Change %": st.column_config.TextColumn("Change %"),
                        "Spend": st.column_config.TextColumn("Spend"),
                        "Sales": st.column_config.TextColumn("Sales"),
                        "ACoS": st.column_config.TextColumn("ACoS"),
                        "Current CPC": st.column_config.TextColumn("Current CPC"),
                        "Projected CPC": st.column_config.TextColumn("Projected CPC"),
                        "VCPM": st.column_config.TextColumn("VCPM"),
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No bid increases to display. Process a file to see top bid increases.")
        
        # Tab for top bid decreases
        with top_targets_tabs[1]:
            if has_decrease_data:
                # Create a DataFrame for top decreases
                top_decreases = st.session_state.analysis_data['top_bid_decreases']
                decreases_df = pd.DataFrame(top_decreases)
                
                # Format the data for display
                decreases_df['old_bid'] = decreases_df['old_bid'].apply(lambda x: f"${x:.2f}")
                decreases_df['new_bid'] = decreases_df['new_bid'].apply(lambda x: f"${x:.2f}")
                decreases_df['change_pct'] = decreases_df['change_pct'].apply(lambda x: f"{x:.1f}%")
                decreases_df['spend'] = decreases_df['spend'].apply(lambda x: f"${x:.2f}")
                decreases_df['sales'] = decreases_df['sales'].apply(lambda x: f"${x:.2f}")
                decreases_df['acos'] = decreases_df['acos'].apply(lambda x: f"{x:.2f}%")
                decreases_df['current_cpc'] = decreases_df['current_cpc'].apply(lambda x: f"${x:.2f}")
                decreases_df['estimated_new_cpc'] = decreases_df['estimated_new_cpc'].apply(lambda x: f"${x:.2f}")
                decreases_df['vcpm'] = decreases_df['vcpm'].apply(lambda x: f"${x:.2f}" if x > 0 else "N/A")
                
                # Rename columns for display
                decreases_df.columns = ['Campaign', 'Target', 'Old Bid', 'New Bid', 'Change %', 'Spend', 'Sales', 'ACoS', 'Current CPC', 'Projected CPC', 'VCPM']
                
                # Display the table with styling
                st.markdown("### Top Bid Decreases")
                st.markdown("These targets received the largest bid decreases:")
                st.dataframe(
                    decreases_df,
                    column_config={
                        "Campaign": st.column_config.TextColumn("Campaign"),
                        "Target": st.column_config.TextColumn("Target", width="large"),
                        "Old Bid": st.column_config.TextColumn("Old Bid"),
                        "New Bid": st.column_config.TextColumn("New Bid"),
                        "Change %": st.column_config.TextColumn("Change %"),
                        "Spend": st.column_config.TextColumn("Spend"),
                        "Sales": st.column_config.TextColumn("Sales"),
                        "ACoS": st.column_config.TextColumn("ACoS"),
                        "Current CPC": st.column_config.TextColumn("Current CPC"),
                        "Projected CPC": st.column_config.TextColumn("Projected CPC"),
                        "VCPM": st.column_config.TextColumn("VCPM"),
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No bid decreases to display. Process a file to see top bid decreases.")
        
        # Individual Sheet Details
        st.subheader("Sheet Details")
        for sheet_name, df in st.session_state.processed_sheets.items():
            with st.expander(f"Sheet: {sheet_name}"):
                st.write(df.head())
                st.write("Rows:", len(df))
                # Sheet-specific metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Sheet Spend", format_currency(df['Spend'].sum()))
                    st.metric("Sheet Sales", format_currency(df['Sales'].sum()))
                
                with col2:
                    if 'ACoS' in df.columns:
                        # Convert ACoS to numeric, coercing errors to NaN, and then calculate mean
                        acos_numeric = pd.to_numeric(df['ACoS'], errors='coerce')
                        st.metric("Sheet Avg ACoS", f"{acos_numeric.mean():.2f}%")
                    else:
                        st.metric("Sheet Avg ACoS", "N/A")
                    
                    # Calculate sheet-level current ACoS
                    if df['Sales'].sum() > 0:
                        current_acos = (df['Spend'].sum() / df['Sales'].sum()) * 100
                        st.metric("Sheet Current ACoS", f"{current_acos:.2f}%")
                
                with col3:
                    # Also ensure Recommended Bid is numeric
                    rec_bid_numeric = pd.to_numeric(df['Recommended Bid'], errors='coerce')
                    st.metric("Sheet Avg Recommended Bid", format_currency(rec_bid_numeric.mean()))
                    
                    # Calculate sheet-level projected ACoS if available
                    if 'Estimated_New_Sales' in df.columns and 'Estimated_New_Spend' in df.columns:
                        est_sales = pd.to_numeric(df['Estimated_New_Sales'], errors='coerce').sum()
                        if est_sales > 0:
                            est_spend = pd.to_numeric(df['Estimated_New_Spend'], errors='coerce').sum()
                            projected_acos = (est_spend / est_sales) * 100
                            st.metric("Sheet Projected ACoS", f"{projected_acos:.2f}%")
                
                # Show a sample of the data
                st.write("Sample Data:")
                st.dataframe(df.head(10))
                
        st.write("---")

st.caption("Built with Streamlit. Converted from Tkinter.")
