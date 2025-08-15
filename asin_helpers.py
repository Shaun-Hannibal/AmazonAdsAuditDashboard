"""
Helper functions for processing and caching ASIN performance data.
"""
import pandas as pd
import streamlit as st
from typing import Dict, Any, Optional, List, Union
import logging

# Set up logging
logger = logging.getLogger(__name__)

def _normalize_asin(asin: str) -> str:
    """Normalize ASIN by converting to string and stripping whitespace."""
    return str(asin).strip().upper()

def _find_matching_asin(asin: str, asin_list: List[str]) -> Optional[str]:
    """Find a matching ASIN in a list, case-insensitively."""
    normalized_asin = _normalize_asin(asin)
    for item in asin_list:
        if _normalize_asin(item) == normalized_asin:
            return item
    return None

def _find_column(df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
    """Find a column in a DataFrame using a list of possible names."""
    for name in possible_names:
        if name in df.columns:
            return name
        
        # Try case-insensitive match
        for col in df.columns:
            if str(col).lower() == name.lower():
                return col
    return None

@st.cache_data(ttl=3600, show_spinner="Processing ASIN performance data...")
def compute_asin_performance(
    bulk_data: Dict[str, pd.DataFrame],
    sales_data: Optional[pd.DataFrame],
    client_config: Dict[str, Any],
    sd_attribution_choice: str = "Sales"
) -> pd.DataFrame:
    """
    Compute and cache ASIN performance metrics from bulk and sales data.
    
    Args:
        bulk_data: Dictionary of bulk data DataFrames
        sales_data: Sales report DataFrame
        client_config: Client configuration dictionary
        sd_attribution_choice: Sales attribution choice for Sponsored Display
        
    Returns:
        DataFrame with ASIN performance metrics
    """
    logger.info("Computing ASIN performance metrics...")
    
    # Combine all bulk data sheets
    bulk_dfs = [df for df in bulk_data.values() if isinstance(df, pd.DataFrame)]
    combined_bulk_df = pd.concat(bulk_dfs, ignore_index=True) if bulk_dfs else pd.DataFrame()
    
    # Initialize records list
    asin_perf_records = []
    
    # Get branded ASINs from config
    branded_asins_data = client_config.get('branded_asins_data', {}) or {}
    
    # Find total sales column in sales report
    total_sales_col = None
    if isinstance(sales_data, pd.DataFrame):
        total_sales_col = _find_column(sales_data, ['Total Sales', 'total sales', 'total_sales'])
    
    # Track all ASINs to process
    all_asins = set()
    
    # Add ASINs from sales report
    if isinstance(sales_data, pd.DataFrame):
        asin_col = _find_column(sales_data, ['ASIN', 'asin', 'child asin', 'parent asin'])
        if asin_col:
            all_asins.update(sales_data[asin_col].dropna().astype(str).str.upper().unique())
    
    # Add ASINs from branded data
    all_asins.update(str(asin).upper() for asin in branded_asins_data.keys())
    
    # Process each ASIN
    for asin in all_asins:
        asin = str(asin).strip().upper()
        if not asin or asin == 'NAN':
            continue
            
        # Initialize ASIN row
        asin_row = {
            'ASIN': asin,
            'Product Group': 'Untagged Group',
            'Product Title': f"Unknown Product ({asin})",
            'Spend': 0,
            'Ad Sales': 0,
            'Total Sales': 0,
            'Clicks': 0,
            'Orders': 0,
            'ACoS': 0,
            'TACoS': 0
        }
        
        # Set product group and title from branded data if available
        branded_info = branded_asins_data.get(asin) or branded_asins_data.get(asin.lower())
        if branded_info:
            asin_row['Product Group'] = branded_info.get('product_group', 'Untagged Group')
            asin_row['Product Title'] = branded_info.get('product_title', f"Unknown Product ({asin})")
        
        # Process bulk data for this ASIN
        if not combined_bulk_df.empty:
            # Find ASIN columns
            asin_columns = [col for col in combined_bulk_df.columns 
                           if 'asin' in str(col).lower()]
            
            # Filter rows for this ASIN
            asin_rows = pd.DataFrame()
            for col in asin_columns:
                mask = (combined_bulk_df[col].astype(str).str.upper() == asin)
                asin_rows = pd.concat([asin_rows, combined_bulk_df[mask]])
            
            if not asin_rows.empty:
                # Sum up metrics
                for metric in ['Spend', 'Clicks', 'Orders']:
                    if metric in asin_rows.columns:
                        asin_row[metric] = asin_rows[metric].sum()
                
                # Handle sales based on product type and attribution
                sd_rows = asin_rows[asin_rows['Product'] == 'Sponsored Display']
                non_sd_rows = asin_rows[asin_rows['Product'] != 'Sponsored Display']
                
                # Process Sponsored Display sales
                if not sd_rows.empty:
                    if sd_attribution_choice == "Sales (Views & Clicks)":
                        sales_col = _find_column(sd_rows, ['Sales (Views & Clicks)', 'sales (views & clicks)'])
                    else:
                        sales_col = _find_column(sd_rows, ['Sales', 'sales'])
                    
                    if sales_col:
                        asin_row['Ad Sales'] += sd_rows[sales_col].sum()
                
                # Process non-Sponsored Display sales
                if not non_sd_rows.empty:
                    sales_col = _find_column(non_sd_rows, ['Sales', 'sales'])
                    if sales_col:
                        asin_row['Ad Sales'] += non_sd_rows[sales_col].sum()
        
        # Get total sales from sales report
        if isinstance(sales_data, pd.DataFrame) and total_sales_col:
            asin_col = _find_column(sales_data, ['ASIN', 'asin'])
            if asin_col:
                mask = (sales_data[asin_col].astype(str).str.upper() == asin)
                asin_row['Total Sales'] = sales_data.loc[mask, total_sales_col].sum()
        
        # Calculate metrics
        if asin_row['Ad Sales'] > 0:
            asin_row['ACoS'] = (asin_row['Spend'] / asin_row['Ad Sales']) * 100
        if asin_row['Total Sales'] > 0:
            asin_row['TACoS'] = (asin_row['Spend'] / asin_row['Total Sales']) * 100
        
        asin_perf_records.append(asin_row)
    
    # Convert to DataFrame
    if not asin_perf_records:
        return pd.DataFrame(columns=['ASIN', 'Product Group', 'Product Title', 'Spend', 'Ad Sales', 
                                   'Total Sales', 'Clicks', 'Orders', 'ACoS', 'TACoS'])
    
    df = pd.DataFrame(asin_perf_records)
    
    # Calculate percentages
    total_spend = df['Spend'].sum()
    total_ad_sales = df['Ad Sales'].sum()
    total_sales = df['Total Sales'].sum()
    
    df['% of Spend'] = (df['Spend'] / total_spend * 100) if total_spend > 0 else 0
    df['% of Ad Sales'] = (df['Ad Sales'] / total_ad_sales * 100) if total_ad_sales > 0 else 0
    df['% of Total Sales'] = (df['Total Sales'] / total_sales * 100) if total_sales > 0 else 0
    
    # Round numeric columns
    for col in ['Spend', 'Ad Sales', 'Total Sales', 'ACoS', 'TACoS', 
                '% of Spend', '% of Ad Sales', '% of Total Sales']:
        if col in df.columns:
            df[col] = df[col].round(2)
    
    return df
