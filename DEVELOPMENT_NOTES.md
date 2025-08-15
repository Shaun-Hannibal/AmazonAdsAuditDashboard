# Amazon Advertising Dashboard - Development Notes

## CRITICAL DEVELOPMENT REQUIREMENTS

### 1. SALES ATTRIBUTION CONSISTENCY
- **All future features** must respect and adapt to the global sales attribution setting selected by the user
- The dashboard has two sales attribution options: "Sales" and "Sales (Views & Clicks)"
- Every new feature that processes or displays sales data must check `st.session_state.sd_attribution_choice`
- For Sponsored Display campaigns, prioritize "Sales (Views & Clicks)" columns when that option is selected
- For all other campaign types or when "Sales" is selected, prioritize standard sales columns

### 2. STREAMLIT RUN REMINDER
- After every code change, always prompt the user to run the Streamlit app in the virtual environment
- Standard command to suggest: `(.venv) shaun@Shannibal-mbp Dashboard % python -m streamlit run app.py`