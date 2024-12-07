import os
import sys
import streamlit as st

# add necessary workspaces

sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))

# update the app 
# before updating the app, upload new data_la_real.txt and secar_daily_data.xlsx
# and run secar_meteo_data_analyzer.py

homepage = st.Page("modules/homepage.py", title = "Home")
current_conditions_page = st.Page("modules/current_conditions_page.py", title = "Current conditions")
daily_summary_page = st.Page("modules/daily_summary_page.py", title = "Daily summary")
recent_data_page = st.Page("modules/recent_data_page.py", title = "Recent data")
historical_data_page = st.Page("modules/historical_data_page.py", title = "Historical data")
annual_comparison_page = st.Page("modules/annual_comparison_page.py", title = "Annual comparison page")
statistics_page = st.Page("modules/statistics_page.py", title = "Statistics")
extreme_data_page = st.Page("modules/extreme_data_page.py", title = "Data extremes")

# for multiple pages in one category, define a dictionary

pg = st.navigation([homepage,
                    current_conditions_page,
                    daily_summary_page,
                    recent_data_page,
                    historical_data_page,
                    annual_comparison_page,
                    statistics_page,
                    extreme_data_page,
                    ]
                  )

pg.run()