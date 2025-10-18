import streamlit as st
from common import load_daily_data,\
                   plot_interactive_data_by_year,\
                   plot_interactive_comparison_cumulative_data, plot_interactive_data_cumsum_by_year


# -----------------------------------MAIN PROGRAM-----------------------------------
st.set_page_config(page_title="Comparativa anual de datos diarios", page_icon="📊", layout="wide")

st.markdown("# Comparativa de datos diarios entre años")
st.write("Esta sección permite comparar los datos diarios entre años. \n \
    Se puede seleccionar una variable y el año de interés. \n ")


# get the data
daily_data = load_daily_data()

st.markdown("## Temperatura diaria")
fig = plot_interactive_data_by_year(daily_data, 'high_temp_deg', "Temperatura máxima diaria", "T (°C)")
st.plotly_chart(fig, use_container_width=True)

fig = plot_interactive_data_by_year(daily_data, 'low_temp_deg', "Temperatura mínima diaria", "T (°C)")
st.plotly_chart(fig, use_container_width=True)

fig = plot_interactive_data_by_year(daily_data, 'temp_out_deg', "Temperatura media diaria", "T (°C)")
st.plotly_chart(fig, use_container_width=True)

st.markdown("## Humedad relativa diaria")
fig = plot_interactive_data_by_year(daily_data, 'max_rel_humidity_perc', "Humedad máxima diaria", "T (°C)")
st.plotly_chart(fig, use_container_width=True)

fig = plot_interactive_data_by_year(daily_data, 'min_rel_humidity_perc', "Humedad mínima diaria", "T (°C)")
st.plotly_chart(fig, use_container_width=True)

fig = plot_interactive_data_by_year(daily_data, 'mean_rel_humidity_perc', "Humedad media diaria", "T (°C)")
st.plotly_chart(fig, use_container_width=True)

st.markdown("## Precipitación diaria")
fig = plot_interactive_data_by_year(daily_data, 'daily_rain_gage_mm', "Precipitación diaria", "mm")
st.plotly_chart(fig, use_container_width=True)

fig = plot_interactive_data_cumsum_by_year(daily_data, 'daily_rain_gage_mm', "Precipitación diaria acumulada", "mm")
st.plotly_chart(fig, use_container_width=True)

fig = plot_interactive_comparison_cumulative_data(daily_data,
                                                  2025,
                                                  'daily_rain_gage_mm',
                                                  'daily_rain_pws_mm',
                                                  'daily_rain_gage_mm',
                                                  "Precipitación diaria acumulada. Comparación entre estación meteorológica y pluviómetro manual",
                                                  "mm")
st.plotly_chart(fig, use_container_width=True)

st.markdown("## Viento diario")
fig = plot_interactive_data_by_year(daily_data, 'wind_speed_kmh', "Velocidad media diaria", "km/h")
st.plotly_chart(fig, use_container_width=True)

fig = plot_interactive_data_by_year(daily_data, 'wind_gust_kmh', "Racha máxima diaria", "km/h")
st.plotly_chart(fig, use_container_width=True)

st.markdown("## Presión barométrica diaria")
fig = plot_interactive_data_by_year(daily_data, 'max_pressure_hPa', "Presión barométrica máxima diaria", "hPa")
st.plotly_chart(fig, use_container_width=True)

fig = plot_interactive_data_by_year(daily_data, 'min_pressure_hPa', "Presión barométrica mínima diaria", "hPa")
st.plotly_chart(fig, use_container_width=True)

fig = plot_interactive_data_by_year(daily_data, 'mean_pressure_hPa', "Presión barométrica media diaria", "hPa")
st.plotly_chart(fig, use_container_width=True)