import streamlit as st
import pandas as pd
import plotly.express as px
from current_conditions_page import _get_current_weather_data
import matplotlib.pyplot as plt


def _select_column_box(data, key):
    # Seleccionar una variable del dataset
    column = st.selectbox("Select a variable to plot", data.columns, key = key)
    return column


def _get_daily_summary(today_data):

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

    daily_summary.rename(columns = {'temperature_deg_max': 'Temperature (°C)',
                                    'humidity_perc_max': 'Humidity (%)',
                                    'wind_gust_kmh': 'Wind gust (km/h)',
                                    'heat_index_deg': 'Heat Index (°C)',
                                    'pressure_max_hPa': 'Pressure (hPa)',
                                    'rain_rate_mmh': 'Rain rate (mm/h)',
                                    'pcp_acum_mm': 'Accumulated precipitation (mm)'}, inplace=True)
    
    daily_summary.drop(['temperature_deg_min', 'humidity_perc_min',
                         'pressure_min_hPa', 'temperature_deg_mean',
                           'humidity_perc_mean'], axis = 1, inplace=True)

    return daily_summary        


def _parse_today_data(today_data):
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


def _plot_interactive_current(data_current, column):
    #Crear gráfico de una variable del dataset para el año 2024
    st.write(f"Interactive daily evolution plot for {column}")
    fig = px.line(data_current, x=data_current.index, y=f"{column}")
    st.plotly_chart(fig)


def _plot_static_current(data_current, column):
    st.write(f"Static daily evolution plot for {column}")

    fig, ax = plt.subplots()
    ax.plot(data_current[column].dropna())
    ax.set_xlabel('date')
    ax.set_ylabel(column)
    ax.grid()
    fig.autofmt_xdate()
    st.pyplot(fig)


def daily_summary_page():

    st.markdown("# Palma Secar de la Real daily summary")

    st.write("Data is updated every 5 minutes. Refresh the page to update.")

    today_data = _get_current_weather_data(mode = 'daily')
    if not(today_data.empty):
        today_data = _parse_today_data(today_data)
        

        daily_summary = _get_daily_summary(today_data)
        st.markdown(f'## Daily summary for {today_data.index[0].date()}')
        st.dataframe(daily_summary)

        st.markdown('## 5 minute data plots')
        column = _select_column_box(today_data, key = "temperature_deg")
        _plot_interactive_current(today_data, column)
        _plot_static_current(today_data, column)

        st.markdown("## 5 minute data in table")
        st.dataframe(today_data)