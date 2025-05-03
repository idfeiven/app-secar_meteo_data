import os
import sys
import streamlit as st

# add necessary workspaces

sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))

# update the app 
# before updating the app, upload new data_la_real.txt and secar_daily_data.xlsx
# and run secar_meteo_data_analyzer.py

homepage = st.Page("modules/homepage.py", title = "Estación meteorológica Secar de la Real - Inicio")
current_conditions_page = st.Page("modules/current_conditions_page.py", title = "Condiciones actuales")
daily_summary_page = st.Page("modules/daily_summary_page.py", title = "Resumen diario")
recent_data_page = st.Page("modules/recent_data_page.py", title = "Datos recientes")
monthly_summary_page = st.Page("modules/monthly_summary_page.py", title = "Resúmenes mensuales")
historical_data_page = st.Page("modules/historical_data_page.py", title = "Histórico")
annual_comparison_page = st.Page("modules/annual_comparison_page.py", title = "Comparativa anual de datos diarios")
extreme_data_page = st.Page("modules/mean_values_page.py", title = "Valores medios mensuales")
extreme_data_page = st.Page("modules/extreme_data_page.py", title = "Valores extremos")
statistics_page = st.Page("modules/statistics_and_rankings_page.py", title = "Valores frecuentes y ránkings") 
indicators_page = st.Page("modules/indicators_page.py", title = "Indicadores climáticos")
# for multiple pages in one category, define a dictionary

pg = st.navigation([homepage,
                    current_conditions_page,
                    daily_summary_page,
                    recent_data_page,
                    historical_data_page,
                    annual_comparison_page,
                    statistics_page,
                    extreme_data_page,
                    indicators_page
                    ]
                  )

pg.run()