import streamlit as st
import pandas as pd
from common import load_daily_data, get_monthly_data

# -----------------------------------MAIN PROGRAM-----------------------------------
st.set_page_config(page_title="Resúmenes mensuales de datos", page_icon="📊", layout="wide")

daily_data = load_daily_data()
daily_data = daily_data.drop(columns=['correction', 'storm', 'daily_rain_pws_mm', 'daily_rain_gage_mm'])

monthly_data = get_monthly_data(daily_data)

st.markdown("## Resúmenes mensuales de datos")
monthly_data.sort_values(by = "date", ascending = False, inplace=True)
monthly_data["date"]= monthly_data["date"].dt.strftime("%Y-%m")
monthly_data = monthly_data.round(2)

k_trans = ["Año y mes",
           'Temperatura máxima mensual (°C)',
           'Ráfaga máxima de viento mensual (km/h)',
           'Máxima lluvia en 10 minutos mensual (mm)',
           'Máxima tasa de lluvia instantánea mensual (mm/h)',
           'Temperatura mínima mensual (°C)',
           "Temperatura media mensual (°C)",
           'Media de las temperaturas máximas (°C)',
           'Media de las temperaturas mínimas (°C)',
           'Humedad relativa media mensual (%)',
           'Punto de rocío medio mensual (°C)',
           'Velocidad media del viento mensual (km/h)',
           'Presión media mensual (hPa)',
           "Precipitación mensual acumulada (mm)",
]

monthly_data.rename(columns = dict(zip(monthly_data.columns, k_trans)), inplace = True)
monthly_data.set_index("Año y mes", inplace = True)

st.dataframe(monthly_data)