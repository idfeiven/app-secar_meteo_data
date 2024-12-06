import streamlit as st
import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))

import daily_summary_page
import recent_data_page
import annual_comparison_page
import historical_data_page
import statistics_page
import extreme_data_page

# Create pages and sidebar
page_names_to_funcs = {
    # "Home": homepage,
    # "Current conditions": current_conditions_page,
    "Daily summary": daily_summary_page,
    "Recent data": recent_data_page,
    "Annual data comparison": annual_comparison_page,
    "Historical data": historical_data_page,
    "Statistics": statistics_page,
    "Data extremes": extreme_data_page
}

demo_name = st.sidebar.selectbox("Choose a page", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]