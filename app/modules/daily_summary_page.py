import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt


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

    daily_mins = today_data.resample('1D').min()[['temperature_deg_min', 'humidity_perc_min',
                                                 'wind_gust_kmh', 'heat_index_deg',
                                                 'pressure_min_hPa', 'rain_rate_mmh', 'pcp_acum_mm']]
    
    daily_maxs = today_data.resample('1D').max()[['temperature_deg_max', 'humidity_perc_max',
                                                 'wind_gust_kmh', 'heat_index_deg',
                                                 'pressure_max_hPa', 'rain_rate_mmh', 'pcp_acum_mm']]
    
    daily_means = today_data.resample('1D').mean()[['temperature_deg_mean', 'humidity_perc_mean',
                                                 'wind_gust_kmh', 'heat_index_deg',
                                                 'pressure_min_hPa', 'rain_rate_mmh', 'pcp_acum_mm']]

    daily_summary = pd.concat([daily_maxs, daily_mins, daily_means], axis = 0)
    daily_summary['Summary'] = ['Max value', 'Min value', 'Mean value']
    daily_summary.set_index('Summary', inplace=True)

    daily_summary.loc['Min value', 'temperature_deg_max'] = daily_summary.loc['Min value', 'temperature_deg_min']
    daily_summary.loc['Mean value', 'temperature_deg_max'] = daily_summary.loc['Mean value', 'temperature_deg_mean']
    daily_summary.loc['Min value', 'humidity_perc_max'] = daily_summary.loc['Min value', 'humidity_perc_min']
    daily_summary.loc['Mean value', 'humidity_perc_max'] = daily_summary.loc['Mean value', 'humidity_perc_mean']
    daily_summary.loc['Min value', 'pressure_max_hPa'] = daily_summary.loc['Min value', 'pressure_min_hPa']
    daily_summary.loc['Mean value', 'pressure_max_hPa'] = daily_summary.loc['Mean value', 'pressure_min_hPa']

    daily_summary.rename(columns = {'temperature_deg_max': 'Temperatura (°C)',
                                    'humidity_perc_max': 'Humedad (%)',
                                    'wind_gust_kmh': 'Ráfaga de viento (km/h)',
                                    'heat_index_deg': 'Índice de calor (°C)',
                                    'pressure_max_hPa': 'Presión (hPa)',
                                    'rain_rate_mmh': 'Tasa de lluvia (mm/h)',
                                    'pcp_acum_mm': 'Precipitación acumulada (mm)'}, inplace=True)
    
    daily_summary.drop(['temperature_deg_min', 'humidity_perc_min',
                         'pressure_min_hPa', 'temperature_deg_mean',
                           'humidity_perc_mean'], axis = 1, inplace=True)

    return daily_summary        


def parse_today_data(today_data):
    today_data = today_data[['obsTimeLocal', 'humidityAvg', 'humidityHigh', 'humidityLow',
                             'metric.tempHigh', 'metric.tempLow', 'metric.tempAvg', 
                             'metric.windspeedAvg', 'metric.heatindexAvg', 'metric.pressureMin',
                             'metric.pressureMax', 'metric.precipRate', 'metric.precipTotal']]
    
    dict_rename = {'obsTimeLocal': 'datetime_local', 'humidityAvg': 'humidity_perc_mean', 'humidityHigh': 'humidity_perc_max',
                'humidityLow': 'humidity_perc_min', 'metric.tempHigh': 'temperature_deg_max', 'metric.tempLow': 'temperature_deg_min',
                'metric.tempAvg': 'temperature_deg_mean', 'metric.windspeedAvg': 'wind_gust_kmh',
                'metric.heatindexAvg': 'heat_index_deg', 'metric.pressureMin': 'pressure_min_hPa', 'metric.pressureMax': 'pressure_max_hPa',
                'metric.precipRate': 'rain_rate_mmh', 'metric.precipTotal': 'pcp_acum_mm'}
    
    today_data = today_data.copy()
    today_data.rename(columns = dict_rename, inplace=True)
    today_data.loc[:, 'datetime_local'] = pd.to_datetime(today_data['datetime_local'])
    today_data.set_index('datetime_local', inplace=True)
    for col in today_data.columns:
        today_data.loc[:, col] = pd.to_numeric(today_data[col])

    return today_data


def plot_interactive_current(data_current, column):
    #Crear gráfico de una variable del dataset para el año 2024
    st.write(f"Interactive daily evolution plot for {column}")
    fig = px.line(data_current, x=data_current.index, y=f"{column}")
    st.plotly_chart(fig)


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