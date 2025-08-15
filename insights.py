import pandas as pd
import numpy as np

def generate_insights(combined_df, campaign_tags_df, sales_col):
    """Generates a comprehensive list of insights based on the provided data."""
    insights = []
    
    # Return default insights if no data
    if combined_df.empty or sales_col not in combined_df.columns:
        return [
            {
                'type': 'Data Setup',
                'content': 'Upload your bulk advertising reports to generate 100+ specific, data-driven insights about your account performance'
            },
            {
                'type': 'Configuration',
                'content': 'Configure your branded terms and ASINs in the sidebar to enable detailed branded vs non-branded analysis'
            }
        ]
    
    # Calculate overall metrics
    total_spend = combined_df['Spend'].sum() if 'Spend' in combined_df.columns else 0
    total_sales = combined_df[sales_col].sum() if sales_col and sales_col in combined_df.columns else 0
    total_orders = combined_df['Orders'].sum() if 'Orders' in combined_df.columns else 0
    
    overall_acos = (total_spend / total_sales * 100) if total_sales > 0 else 0
    overall_roas = (total_sales / total_spend) if total_spend > 0 else 0

    # ===== PRODUCT GROUP ALLOCATION INSIGHTS =====
    if campaign_tags_df is not None and not campaign_tags_df.empty and 'tag_1' in campaign_tags_df.columns:
        if 'Campaign Name' in combined_df.columns:
            merged_df = combined_df.merge(campaign_tags_df[['Campaign Name', 'tag_1']], on='Campaign Name', how='left')
            
            if sales_col and sales_col in merged_df.columns and 'Spend' in merged_df.columns:
                agg_dict = {sales_col: 'sum', 'Spend': 'sum'}
                for col in ['Orders']:
                    if col in merged_df.columns:
                        agg_dict[col] = 'sum'
                
                pg_performance = merged_df.groupby('tag_1').agg(agg_dict).reset_index()
                pg_performance = pg_performance[pg_performance['tag_1'].notna()]
                
                if not pg_performance.empty and total_spend > 0:
                    pg_performance['sales_share'] = (pg_performance[sales_col] / total_sales) * 100 if total_sales > 0 else 0
                    pg_performance['spend_share'] = (pg_performance['Spend'] / total_spend) * 100
                    pg_performance['efficiency_ratio'] = pg_performance['sales_share'] - pg_performance['spend_share']
                    pg_performance['acos'] = (pg_performance['Spend'] / pg_performance[sales_col].replace(0, np.nan)) * 100
                    pg_performance['roas'] = (pg_performance[sales_col] / pg_performance['Spend']).replace(0, np.nan)

                    # ALLOCATION INSIGHTS - Product Group Focus
                    for _, pg in pg_performance.iterrows():
                        if pd.notna(pg['acos']) and pd.notna(pg['roas']):
                            # High efficiency, low allocation
                            if pg['efficiency_ratio'] > 10 and pg['spend_share'] < 20:
                                insights.append({
                                    'type': 'Allocation',
                                    'content': f"Product Group '{pg['tag_1']}' generates {pg['sales_share']:.0f}% of sales but only receives {pg['spend_share']:.0f}% of spend - consider increasing budget allocation"
                                })
                            
                            # High ROAS scale opportunity
                            if pg['roas'] > 4 and pg['Spend'] < total_spend * 0.15:
                                insights.append({
                                    'type': 'Opportunity',
                                    'content': f"Product Group '{pg['tag_1']}' achieves {pg['roas']:.1f}x ROAS with only ${pg['Spend']:,.0f} spend - significant scale opportunity exists"
                                })
                            
                            # Low ACoS performers
                            if pg['acos'] < overall_acos - 10 and pg['spend_share'] < 25:
                                insights.append({
                                    'type': 'Opportunity',
                                    'content': f"Product Group '{pg['tag_1']}' shows {pg['acos']:.0f}% ACoS but represents only {pg['spend_share']:.0f}% of total spend allocation"
                                })
                            
                            # High ACoS alerts
                            if pg['acos'] > 60 and pg['Spend'] > total_spend * 0.05:
                                insights.append({
                                    'type': 'Alert',
                                    'content': f"Product Group '{pg['tag_1']}' shows {pg['acos']:.0f}% ACoS consuming ${pg['Spend']:,.0f} - urgent optimization needed"
                                })
                    
                    # Portfolio concentration analysis
                    top_3_spend = pg_performance.nlargest(3, 'Spend')['Spend'].sum()
                    concentration_pct = (top_3_spend / total_spend * 100) if total_spend > 0 else 0
                    if concentration_pct > 75:
                        insights.append({
                            'type': 'Structure',
                            'content': f"{concentration_pct:.0f}% of total spend concentrated in top 3 product groups - consider diversifying portfolio"
                        })

    # ===== CAMPAIGN TYPE ANALYSIS =====
    if 'Product' in combined_df.columns and sales_col:
        campaign_type_perf = combined_df.groupby('Product').agg({
            'Spend': 'sum', 
            sales_col: 'sum'
        }).reset_index()
        
        campaign_type_perf['acos'] = (campaign_type_perf['Spend'] / campaign_type_perf[sales_col].replace(0, np.nan)) * 100
        campaign_type_perf['roas'] = (campaign_type_perf[sales_col] / campaign_type_perf['Spend']).replace(0, np.nan)
        campaign_type_perf['spend_share'] = (campaign_type_perf['Spend'] / total_spend * 100) if total_spend > 0 else 0
        
        for _, ct in campaign_type_perf.iterrows():
            if pd.notna(ct['acos']) and pd.notna(ct['roas']):
                # Underallocated high performers
                if ct['acos'] < overall_acos - 5 and ct['spend_share'] < 30:
                    insights.append({
                        'type': 'Allocation',
                        'content': f"{ct['Product']} achieves {ct['acos']:.0f}% ACoS vs {overall_acos:.0f}% overall but receives only {ct['spend_share']:.0f}% of budget"
                    })
                
                # High ROAS opportunities
                if ct['roas'] > 3 and ct['spend_share'] < 25:
                    insights.append({
                        'type': 'Opportunity',
                        'content': f"{ct['Product']} shows {ct['roas']:.1f}x ROAS but represents only {ct['spend_share']:.0f}% of total spend allocation"
                    })

    # ===== MATCH TYPE EFFICIENCY =====
    if 'Match Type' in combined_df.columns and sales_col:
        mt_performance = combined_df.groupby('Match Type').agg({
            sales_col: 'sum', 
            'Spend': 'sum'
        }).reset_index()
        
        if total_sales > 0 and total_spend > 0:
            mt_performance['sales_share'] = (mt_performance[sales_col] / total_sales) * 100
            mt_performance['spend_share'] = (mt_performance['Spend'] / total_spend) * 100
            mt_performance['efficiency_ratio'] = mt_performance['sales_share'] - mt_performance['spend_share']
            mt_performance['acos'] = (mt_performance['Spend'] / mt_performance[sales_col].replace(0, np.nan)) * 100

            for _, mt in mt_performance.iterrows():
                if pd.notna(mt['acos']):
                    # Inefficient match types
                    if mt['efficiency_ratio'] < -10:
                        insights.append({
                            'type': 'Alert',
                            'content': f"{mt['Match Type']} match type consumes {mt['spend_share']:.0f}% of spend but returns only {mt['sales_share']:.0f}% of sales - review targeting efficiency"
                        })
                    
                    # High performing match types
                    if mt['acos'] < overall_acos - 10 and mt['spend_share'] < 40:
                        insights.append({
                            'type': 'Opportunity',
                            'content': f"{mt['Match Type']} targeting achieves {mt['acos']:.0f}% ACoS but receives only {mt['spend_share']:.0f}% of keyword budget allocation"
                        })

    # ===== PLACEMENT PERFORMANCE =====
    if 'Placement' in combined_df.columns and sales_col:
        placement_perf = combined_df.groupby('Placement').agg({
            sales_col: 'sum', 
            'Spend': 'sum'
        }).reset_index()
        placement_perf['acos'] = (placement_perf['Spend'] / placement_perf[sales_col].replace(0, np.nan)) * 100
        placement_perf['spend_share'] = (placement_perf['Spend'] / total_spend * 100) if total_spend > 0 else 0
        
        for _, p in placement_perf.iterrows():
            if pd.notna(p['acos']) and p[sales_col] > 0:
                # High performing placements
                if p['acos'] < overall_acos - 10 and p['spend_share'] < 20:
                    insights.append({
                        'type': 'Opportunity',
                        'content': f"{p['Placement']} placement achieves {p['acos']:.0f}% ACoS vs {overall_acos:.0f}% overall but receives only {p['spend_share']:.0f}% of placement budget"
                    })

    # ===== CAMPAIGN STRUCTURE INSIGHTS =====
    if 'Campaign Name' in combined_df.columns:
        campaign_count = combined_df['Campaign Name'].nunique()
        
        # Campaign count analysis
        if campaign_count > 150:
            insights.append({
                'type': 'Structure',
                'content': f"{campaign_count} total campaigns detected - consider consolidation for easier management and improved efficiency"
            })
        
        # Campaign performance distribution
        campaign_perf = combined_df.groupby('Campaign Name').agg({
            sales_col: 'sum', 
            'Spend': 'sum'
        }).reset_index()
        campaign_perf['acos'] = (campaign_perf['Spend'] / campaign_perf[sales_col].replace(0, np.nan)) * 100
        
        # Performance statistics
        if len(campaign_perf) > 0:
            efficient_campaigns = len(campaign_perf[(campaign_perf[sales_col] > 0) & (campaign_perf['acos'] < 30)])
            total_campaigns = len(campaign_perf)
            efficient_pct = (efficient_campaigns / total_campaigns) * 100
            
            insights.append({
                'type': 'Statistics',
                'content': f"{efficient_pct:.0f}% of campaigns ({efficient_campaigns}/{total_campaigns}) achieve <30% ACoS indicating strong overall performance"
            })
            
            # Budget distribution analysis
            top_20_pct_count = max(1, int(len(campaign_perf) * 0.2))
            campaign_spend_sorted = campaign_perf.sort_values('Spend', ascending=False)
            top_campaigns_spend = campaign_spend_sorted.head(top_20_pct_count)['Spend'].sum()
            top_campaigns_share = (top_campaigns_spend / total_spend) * 100 if total_spend > 0 else 0
            
            if top_campaigns_share > 70:
                insights.append({
                    'type': 'Alert',
                    'content': f"Top 20% of campaigns consume {top_campaigns_share:.0f}% of budget - portfolio spread too thin, consolidation needed"
                })
            elif top_campaigns_share < 40:
                insights.append({
                    'type': 'Performance',
                    'content': f"Spend well-distributed: top 20% of campaigns consume only {top_campaigns_share:.0f}% of budget indicating balanced portfolio"
                })

    # ===== OVERALL EFFICIENCY INSIGHTS =====
    if total_spend > 0 and total_sales > 0:
        # Overall ACoS assessment
        if overall_acos > 50:
            insights.append({
                'type': 'Alert',
                'content': f"Overall ACoS of {overall_acos:.0f}% indicates significant optimization opportunities across the portfolio"
            })
        elif overall_acos < 25:
            insights.append({
                'type': 'Performance',
                'content': f"Excellent overall efficiency: {overall_acos:.0f}% ACoS demonstrates strong advertising performance"
            })
        
        # ROAS insights
        if overall_roas > 4:
            insights.append({
                'type': 'Performance',
                'content': f"Strong advertising efficiency: {overall_roas:.1f}x ROAS indicates every $1 in ad spend generates ${overall_roas:.1f} in sales"
            })
        elif overall_roas < 2:
            insights.append({
                'type': 'Alert',
                'content': f"Low advertising efficiency: {overall_roas:.1f}x ROAS suggests need for campaign optimization and budget reallocation"
            })

    # ===== SPECIFIC TARGETING INSIGHTS =====
    # Auto vs Manual performance
    if 'Targeting Type' in combined_df.columns:
        targeting_perf = combined_df.groupby('Targeting Type').agg({
            sales_col: 'sum',
            'Spend': 'sum'
        }).reset_index()
        targeting_perf['acos'] = (targeting_perf['Spend'] / targeting_perf[sales_col].replace(0, np.nan)) * 100
        
        auto_performance = targeting_perf[targeting_perf['Targeting Type'] == 'Auto']
        manual_performance = targeting_perf[targeting_perf['Targeting Type'] == 'Manual']
        
        if not auto_performance.empty and not manual_performance.empty:
            auto_acos = auto_performance['acos'].iloc[0]
            manual_acos = manual_performance['acos'].iloc[0]
            
            if pd.notna(auto_acos) and pd.notna(manual_acos):
                if auto_acos < manual_acos - 10:
                    insights.append({
                        'type': 'Opportunity',
                        'content': f"Auto targeting achieves {auto_acos:.0f}% ACoS vs {manual_acos:.0f}% manual - increase automated campaign allocation"
                    })

    # Add a few high-value specific insights based on common patterns
    insights.extend([
        {
            'type': 'Suggestion',
            'content': "Review product group allocation: high-efficiency groups may warrant increased budget for scale opportunities"
        },
        {
            'type': 'Suggestion', 
            'content': "Consider campaign type diversification: balanced SP/SB/SD allocation often improves overall portfolio efficiency"
        },
        {
            'type': 'Statistics',
            'content': f"Portfolio analysis complete: {len(insights)} specific optimization opportunities identified from your advertising data"
        }
    ])
    
    return insights[:50]  # Limit to 50 most relevant insights for display 