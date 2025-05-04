import time
import requests
import pandas as pd
import streamlit as st

#--------------------------------FUNCTIONS----------------------------------#

def _get_url_api_wu(mode): #set mode. Accepts current, daily
    station_id = 'IPALMA141' #select a station id from Weather Underground
    api_key = 'd4a43e6d3abf4b17a43e6d3abfdb1772' #introduce your api key        
    if mode == 'current':
        url_pws = f"https://api.weather.com/v2/pws/observations/current?stationId={station_id}&format=json&units=m&apiKey={api_key}&numericPrecision=decimal"
    elif mode == 'daily':
        url_pws = f"https://api.weather.com/v2/pws/observations/all/1day?stationId={station_id}&format=json&units=m&apiKey={api_key}&numericPrecision=decimal"

    return(url_pws)


def get_current_weather_data(mode): #set mode. Accepts current, daily

    url_pws = _get_url_api_wu(mode = mode)            
    response = requests.get(url_pws)

    if response.status_code == 200:
        current_data = response.json()
        current_data = pd.json_normalize(current_data['observations'])
        return current_data
    else:
        st.write("Failed to retrieve weather data")
        return pd.DataFrame()


def show_current_weather_data(current_data):
    if not(current_data.empty):
        st.write(f"Última observación: {current_data['obsTimeLocal'][0]}")
        col1, col2, col3 = st.columns(3) #crear 3 columnas
        
        col1.metric("Temperatura (°C)", current_data['metric.temp']) #mostrar datos como métrica
        col2.metric("Humedad (%)", current_data['humidity'])            
        col3.metric("Ráfaga de viento últimos 10 min (km/h)", current_data['metric.windSpeed'])

        col1, col2, col3 = st.columns(3)

        col1.metric("Presión (hPa)", current_data['metric.pressure'])            
        col2.metric("Precipitación diaria (mm)", current_data['metric.precipTotal'])
        col3.metric("Tasa de lluvia (mm/h)", current_data['metric.precipRate'])


#--------------------------------MAIN PROGRAM----------------------------------#
st.set_page_config(page_title="Condiciones actuales", page_icon="🌤️", layout="wide")

st.markdown("## Condiciones actuales")
st.write("Datos obtenidos de la API web de Wunderground. Intervalo de actualización: 20 segundos")

while True:
    current_data = get_current_weather_data(mode = 'current')  
    placeholder = st.empty()
    with placeholder.container():
        show_current_weather_data(current_data)
    time.sleep(20)
    placeholder.empty()