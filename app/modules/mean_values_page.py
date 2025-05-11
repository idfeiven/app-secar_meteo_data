import streamlit as st
import pandas as pd
import numpy as np
from common import load_daily_data, get_monthly_data, plot_interactive_data_by_year


# -----------------------------------FUNCTIONS-----------------------------------

def get_monthly_data_means(monthly_data):
    monthly_data_means = monthly_data.groupby(monthly_data['date'].dt.strftime('%m')).mean()\
        .drop(['Temperatura máxima mensual (°C)',
               'Racha de viento máxima mensual (km/h)',
               'Precipitación máxima 10-minutal (mm)',
               'Máxima intensidad de lluvia (mm/h)',
               'Temperatura mínima mensual (°C)'], axis = 1)
    
    return(monthly_data_means)


# -----------------------------------MAIN PROGRAM-----------------------------------

st.set_page_config(page_title="Valores medios mensuales", page_icon=":bar_chart:", layout="wide")
st.title("Valores medios mensuales")

daily_data = load_daily_data()
monthly_data = get_monthly_data(daily_data)
monthly_data_means = get_monthly_data_means(monthly_data)
monthly_data.set_index('date', inplace = True)
monthly_data_means.set_index('date', inplace = True)


st.markdown("## Temperatura mensual")
fig = plot_interactive_data_by_year(monthly_data, 'Media mensual de temperaturas máximas (°C)', "Temperatura máxima media mensual", "T (°C)")
st.plotly_chart(fig, use_container_width=True)

fig = plot_interactive_data_by_year(monthly_data, 'Media mensual de temperaturas mínimas (°C)', "Temperatura mínima media mensual", "T (°C)")
st.plotly_chart(fig, use_container_width=True)

fig = plot_interactive_data_by_year(monthly_data, 'Temperatura media mensual (°C)', "Temperatura media mensual", "T (°C)")
st.plotly_chart(fig, use_container_width=True)

st.markdown("## Precipitación mensual y anual")
fig = plot_interactive_data_by_year(monthly_data, 'Precipitación mensual (mm)', "Precipitación acumulada mensual", "mm")
st.plotly_chart(fig, use_container_width=True)

st.markdown("## Valores medios mensuales en tabla")
# monthly_data_means.drop("date", axis = 1, inplace=True)
monthly_data_means.reset_index(inplace = True)
monthly_data_means.drop("date", axis = 1, inplace=True)
# monthly_data_means.rename(columns={"date": "Month"}, inplace=True)
monthly_data_means["Month"] = np.arange(1,13)
monthly_data_means.set_index("Month", inplace=True)
monthly_data_means = monthly_data_means.round(2)


k_trans = ["Temperatura Media (°C)",
           "Media de Temperaturas Máximas (°C)",
           "Media de Temperaturas Mínimas (°C)",
           "Humedad Relativa Media (%)",
           "Temperatura Media de Punto de Rocío (°C)",
           "Velocidad Media del Viento (km/h)",
           "Presión Media al Nivel del Mar (hPa)",
           "Precipitación Media (mm)"]

monthly_data_means.rename(columns = dict(zip(monthly_data_means.columns, k_trans)), inplace=True)
st.dataframe(monthly_data_means)