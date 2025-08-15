# Active Context: Amazon Advertising Dashboard

## Current Focus
Implementing global sales attribution functionality across all dashboard sections

## Immediate Goals
1. Ensure all dashboard sections respect the global sales attribution setting
2. Maintain consistent sales data display across all reports and visualizations
3. Continue improving dashboard usability and performance

## Session Started
2025-04-14 02:35 AM

## CRITICAL DEVELOPMENT REQUIREMENTS

### 1. SALES ATTRIBUTION CONSISTENCY
- **All future features** must respect and adapt to the global sales attribution setting selected by the user
- The dashboard has two sales attribution options: "Sales" and "Sales (Views & Clicks)"
- Every new feature that processes or displays sales data must check `st.session_state.sd_attribution_choice`
- For Sponsored Display campaigns, prioritize "Sales (Views & Clicks)" columns when that option is selected
- For all other campaign types or when "Sales" is selected, prioritize standard sales columns

### 2. STREAMLIT RUN REMINDER
- After every code change, always prompt the user to run the Streamlit app in the virtual environment
- Standard command to suggest: `cd /Users/shaun/Documents/Python Projects/Dashboard && python -m streamlit run app.py`
- Never assume the app will auto-reload; always explicitly remind the user to restart the app

## Recent Changes
- Moved sales attribution radio button from Account Overview section to global dashboard level
- Updated targeting performance, branded campaign classification, and KPI calculation functions to use global setting
- Implemented consistent sales column prioritization based on user selection
