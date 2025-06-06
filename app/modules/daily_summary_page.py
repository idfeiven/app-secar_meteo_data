import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt

#--------------------------------FUNCTIONS----------------------------------#

def _get_url_api_wu(mode): #set mode. Accepts current, daily
    station_id = 'IPALMA141' #select a station id from Weather Underground
    api_key = 'd4a43e6d3abf4b17a43e6d3abfdb1772' #introduce your api key        
    if mode == 'current':
        url_pws = f"https://api.weather.com/v2/pws/observations/current?stationId={station_id}&format=json&units=m&apiKey={api_key}&numericPrecision=decimal"
    elif mode == 'daily':
        url_pws = f"https://api.weather.com/v2/pws/observations/all/1day?stationId={station_id}&format=json&units=m&apiKey={api_key}&numericPrecision=decimal"

    return(url_pws)


def select_column_box(data, key):
    # Seleccionar una variable del dataset
    column = st.selectbox("Select a variable to plot", data.columns, key = key)
    return column

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


def get_daily_summary(today_data):

    daily_mins = today_data.resample('1D').min()[['Temperatura mínima', 'Humedad mínima',
                                                 'Ráfaga viento km/h', 'Índice calor',
                                                 'Presión mínima hPa', 'Tasa lluvia mm/h', 'Precipitación acumulada mm']]
    
    daily_maxs = today_data.resample('1D').max()[['Temperatura máxima', 'Humedad máxima',
                                                 'Ráfaga viento km/h', 'Índice calor',
                                                 'Presión máxima hPa', 'Tasa lluvia mm/h', 'Precipitación acumulada mm']]
    
    daily_means = today_data.resample('1D').mean()[['Temperatura media', 'Humedad media',
                                                 'Ráfaga viento km/h', 'Índice calor',
                                                 'Presión mínima hPa', 'Tasa lluvia mm/h', 'Precipitación acumulada mm']]

    daily_summary = pd.concat([daily_maxs, daily_mins, daily_means], axis = 0)
    daily_summary['Resumen'] = ['Valor máximo', 'Valor mínimo', 'Valor medio']
    daily_summary.set_index('Resumen', inplace=True)

    return daily_summary        


def parse_today_data(today_data):
    today_data = today_data[['obsTimeLocal', 'humidityAvg', 'humidityHigh', 'humidityLow',
                             'metric.tempHigh', 'metric.tempLow', 'metric.tempAvg', 
                             'metric.windspeedAvg', 'metric.heatindexAvg', 'metric.pressureMin',
                             'metric.pressureMax', 'metric.precipRate', 'metric.precipTotal']]
    
    dict_rename = {'obsTimeLocal': 'Fecha y hora local', 
                   'humidityAvg': 'Humedad media', 
                   'humidityHigh': 'Humedad máxima',
                   'humidityLow': 'Humedad mínima', 
                   'metric.tempHigh': 'Temperatura máxima', 
                   'metric.tempLow': 'Temperatura mínima',
                   'metric.tempAvg': 'Temperatura media', 
                   'metric.windspeedAvg': 'Ráfaga viento km/h',
                   'metric.heatindexAvg': 'Índice calor', 
                   'metric.pressureMin': 'Presión mínima hPa', 
                   'metric.pressureMax': 'Presión máxima hPa',
                   'metric.precipRate': 'Tasa lluvia mm/h', 
                   'metric.precipTotal': 'Precipitación acumulada mm'}
    
    today_data = today_data.copy()
    today_data.rename(columns = dict_rename, inplace=True)
    today_data.loc[:, 'Fecha y hora local'] = pd.to_datetime(today_data['Fecha y hora local'])
    today_data.set_index('Fecha y hora local', inplace=True)
    for col in today_data.columns:
        today_data.loc[:, col] = pd.to_numeric(today_data[col])

    return today_data


def plot_interactive_current(data_current, column):
    #Crear gráfico de una variable del dataset para el año 2024
    st.write(f"Interactive daily evolution plot for {column}")
    fig = px.line(data_current, x=data_current.index, y=f"{column}")
    st.plotly_chart(fig)

# -----------------------------------MAIN PROGRAM-----------------------------------
st.set_page_config(page_title="Resumen diario de Palma Secar de la Real", page_icon="📊", layout="wide")

st.markdown("# Resumen diario de Palma Secar de la Real")

st.write("Los datos se actualizan cada 5 minutos. Actualiza la página para obtener los datos más recientes.")

today_data = get_current_weather_data(mode = 'daily')
if not(today_data.empty):
    today_data = parse_today_data(today_data)
    

    daily_summary = get_daily_summary(today_data)
    st.markdown(f'## Resumen diario para el día {today_data.index[0].date()}')
    st.dataframe(daily_summary)

    st.markdown('## Gráficas de datos 5-minutales')
    column = select_column_box(today_data, key = "temperature_deg")
    plot_interactive_current(today_data, column)

    st.markdown("## Datos 5-minutales en tabla")
    st.dataframe(today_data)