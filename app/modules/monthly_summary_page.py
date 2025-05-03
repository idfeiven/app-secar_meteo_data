import streamlit as st
import pandas as pd
from common import load_daily_data, get_monthly_data

# -----------------------------------MAIN PROGRAM-----------------------------------
daily_data = load_daily_data()
monthly_data = get_monthly_data(daily_data)

st.markdown("## Resúmenes mensuales de datos")
monthly_data = monthly_data.copy()
monthly_data['date'] = monthly_data.index
monthly_data = monthly_data.reset_index(drop=True)
monthly_data.sort_values(by = "date", ascending = False, inplace=True)
monthly_data["date"]= monthly_data["date"].dt.strftime("%Y-%m")
monthly_data = monthly_data.round(2)

monthly_data.rename(columns = {'date': "Año y mes",
                               'max_high_temp_deg': 'Temperatura máxima mensual (°C)',
                               'max_wind_gust_kmh': 'Ráfaga máxima de viento mensual (km/h)',
                               'max_rain_10min_mm': 'Máxima lluvia en 10 minutos mensual (mm)',
                               'max_rain_rate_mmh': 'Máxima tasa de lluvia instantánea mensual (mm/h)',
                               'mean_temp_out_deg': 'Temperatura media mensual (°C)',
                               'min_low_temp_deg': "Temperatura mínima mensual (°C)",
                               'pcp_acum_month_mm': "Precipitación mensual acumulada (mm)",
                               'mean_high_temp_deg': 'Temperatura máxima media mensual (°C)',
                               'mean_low_temp_deg': 'Temperatura mínima media mensual (°C)',
                               'mean_rel_humidity_perc': 'Humedad relativa media mensual (%)',
                               'mean_dewpoint_deg': 'Punto de rocío medio mensual (°C)',
                               'mean_wind_speed_kmh': 'Velocidad media del viento mensual (km/h)',
                               'mean_pressure_hPa': 'Presión media mensual (hPa)'}, inplace = True)
monthly_data.set_index("Year and month", inplace = True)

st.dataframe(monthly_data)