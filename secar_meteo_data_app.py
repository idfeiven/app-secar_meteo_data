import streamlit as st
import pandas as pd
import plotly.express as px
import os
import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import requests
import time
import warnings
import numpy as np

warnings.filterwarnings(action = 'ignore', category = FutureWarning)

#todo add rest of figures from secar_meteo_data_analyzer.py

# 3rd order functions

def __get_url_api_wu(mode): #set mode. Accepts current, daily
    station_id = 'IPALMA141' #select a station id from Weather Underground
    api_key = 'd4a43e6d3abf4b17a43e6d3abfdb1772' #introduce your api key        
    if mode == 'current':
        url_pws = f"https://api.weather.com/v2/pws/observations/current?stationId={station_id}&format=json&units=m&apiKey={api_key}&numericPrecision=decimal"
    elif mode == 'daily':
        url_pws = f"https://api.weather.com/v2/pws/observations/all/1day?stationId={station_id}&format=json&units=m&apiKey={api_key}&numericPrecision=decimal"

    return(url_pws)


def __get_url_api_wu_hist(date_str):
    station_id = 'IPALMA141' #select a station id from Weather Underground
    api_key = 'd4a43e6d3abf4b17a43e6d3abfdb1772' #introduce your api key     
    url_pws_hist = f"https://api.weather.com/v2/pws/history/all?stationId={station_id}&format=json&units=m&date={date_str}&apiKey={api_key}&numericPrecision=decimal"

    return(url_pws_hist)

# 2nd order Functions

def _get_current_weather_data(mode): #set mode. Accepts current, daily

    url_pws = __get_url_api_wu(mode = mode)            
    response = requests.get(url_pws)

    if response.status_code == 200:
        current_data = response.json()
        current_data = pd.json_normalize(current_data['observations'])
        return current_data
    else:
        st.write("Failed to retrieve weather data")
        return pd.DataFrame()


def _show_current_weather_data(current_data):
    if not(current_data.empty):
        st.write(f"Last observation: {current_data['obsTimeLocal'][0]}")
        col1, col2, col3 = st.columns(3) #create 3 columns
        
        col1.metric("Temperature (°C)", current_data['metric.temp']) #display data as a metric
        col2.metric("Humidity (%)", current_data['humidity'])            
        col3.metric("Wind gust last 10 min (km/h)", current_data['metric.windSpeed'])

        col1, col2, col3 = st.columns(3)

        col1.metric("Pressure (hPa)", current_data['metric.pressure'])            
        col2.metric("Daily precipitation (mm)", current_data['metric.precipTotal'])
        col3.metric("Rain rate (mm/h)", current_data['metric.precipRate'])


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


def _select_column_box(data, key):
    # Seleccionar una variable del dataset
    column = st.selectbox("Select a variable to plot", data.columns, key = key)
    return column


def _select_history_data_type(key = "Daily data"):
    #Seleccionar el tipo de datos históricos a representar
    data_type = st.selectbox("Select data type to plot", ["10-min data", "Daily data"], key = key)
    if data_type == "Daily data":
        daily_data = _load_daily_data()
        return daily_data
    elif data_type == "10-min data":
        raw_data = _load_10min_data()
        raw_data['pcp (mm)'] = np.nan
        raw_data['daily_rain_mm'] = np.nan
        return raw_data


def _filter_current_data(data):
    data_current = data[data.index.year == datetime.datetime.now().year]
    return data_current


def _get_map_data():
    #Mostrar en un mapa la ubicación de la estación
    map_data = pd.DataFrame(
        [[39.6073994131482, 2.638403533715773]],
        columns=['lat', 'lon'])
    return map_data


# Cargar el dataset desde un archivo local
@st.cache_data
def _load_daily_data():
    fpath = os.getcwd() +  r'/secar_daily_data.xlsx'
    daily_data = pd.read_excel(fpath)
    daily_data = daily_data.drop('Unnamed: 0', axis = 1)
    daily_data.set_index('date', inplace = True)
    return daily_data


@st.cache_data
def _load_10min_data():
    fpath = os.getcwd() +  r'/secar_10min_data.xlsx'
    daily_data = pd.read_excel(fpath)
    daily_data = daily_data.drop('Unnamed: 0', axis = 1)
    daily_data.set_index('date', inplace = True)
    return daily_data


def _get_wind_data(raw_data):
    wind_data = raw_data[raw_data["wind_speed_kmh"] > 0.0][["wind_speed_kmh", "wind_direction"]]
    wind_data["wind_direction"] = pd.Categorical(wind_data["wind_direction"], ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"])
    wind_data.sort_values("wind_direction", inplace=True)

    return wind_data

def _get_df_wind_rose(wind_data):
    bins = np.arange(0.0, wind_data.wind_speed_kmh.max() + 5, 5)
    wind_data['10-min average wind speed (km/h)'] = pd.cut(wind_data['wind_speed_kmh'], bins)
    wind_rose = wind_data.groupby(["10-min average wind speed (km/h)", "wind_direction"]).count().reset_index()
    wind_rose["frequency"] = wind_rose["wind_speed_kmh"]/len(wind_data)

    return wind_rose

def _plot_interactive_wind_rose(wind_rose):

    fig = px.bar_polar(wind_rose, r = "frequency", theta="wind_direction",
                   color="10-min average wind speed (km/h)", template="plotly_dark",
                   color_discrete_sequence= px.colors.sequential.Viridis,
                   width = 1200,
                   height = 1000)
    
    st.plotly_chart(fig)


def _get_monthly_data(daily_data):
    #resample daily data to monthly data:
    max_monthly_data = daily_data.resample('m').max()\
                        [['high_temp_deg', 'wind_gust_kmh', 'rain_10min_mm', 'rain_rate_mmh']]\
                        .rename(columns = {'high_temp_deg': 'max_high_temp_deg',
                                           'wind_gust_kmh': 'max_wind_gust_kmh',
                                           'rain_10min_mm': 'max_rain_10min_mm',
                                           'rain_rate_mmh': 'max_rain_rate_mmh'})

    min_monthly_data = daily_data.resample('m').min()[['low_temp_deg']]\
        .rename(columns= {'low_temp_deg': 'min_low_temp_deg'})

    mean_monthly_data = daily_data\
        .resample('m').mean()[['temp_out_deg', 'high_temp_deg', 'low_temp_deg' ,'rel_humidity_perc', 'dewpoint_deg', 'wind_speed_kmh', 'pressure_hPa']]\
        .rename(columns={'temp_out_deg': 'mean_temp_out_deg',
                         'high_temp_deg': 'mean_high_temp_deg',
                         'low_temp_deg': 'mean_low_temp_deg',
                         'rel_humidity_perc': 'mean_rel_humidity_perc',
                         'dewpoint_deg': 'mean_dewpoint_deg',
                         'wind_speed_kmh': 'mean_wind_speed_kmh',
                         'pressure_hPa': 'mean_pressure_hPa'})

    monthly_pcp_data = daily_data.resample('m').sum()[['pcp (mm)']]
    #group all monthly data
    monthly_data = pd.concat([max_monthly_data, min_monthly_data, mean_monthly_data, monthly_pcp_data], axis = 1).rename(columns = {'pcp (mm)': 'pcp_acum_month_mm'})
    monthly_data = monthly_data.reset_index()  
    return(monthly_data) 


def _get_monthly_data_means(monthly_data):
    monthly_data_means = monthly_data.groupby(monthly_data['date'].dt.strftime('%m')).mean()\
        .drop(['max_high_temp_deg', 'max_wind_gust_kmh', 'max_rain_10min_mm', 'max_rain_rate_mmh',
                'min_low_temp_deg'], axis = 1).rename(columns = {'pcp_acum_month_mm': 'mean_pcp_acum_month_mm'})
    return(monthly_data_means)


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


def _get_df_variable_description(data):
    var_description = ["Daily accumulated precipitation from manual rain gauge",
                    "Daily maximum temperature in degrees Celsius",
                    "Daily maximum wind gust in km/h",
                    "Daily maximum 10-min rain accumulation from automatic rain gauge",
                    "Daily maximum rain rate from automatic rain gauge",
                    "Daily minimum temperature in degrees Celsius",
                    "Daily accumulated precipitation from automatic rain gauge",
                    "Daily mean temperature in degrees Celsius",
                    "Daily mean relative humidity",
                    "Daily mean dewpoint in degrees Celsius",
                    "Daily mean wind speed in km/h",
                    "Daily mean pressure in hPa"
                    ]
    var_validity = ["2014-01-11",
                    "2021-02-06",
                    "2021-02-06",
                    "2021-02-06",
                    "2021-02-06",
                    "2021-02-06",
                    "2021-02-06",
                    "2021-02-06",
                    "2021-02-06",
                    "2021-02-06",
                    "2021-02-06",
                    "2021-02-06"]
    df_var_descr = pd.DataFrame(var_description, columns=['Description'])
    df_cols = pd.DataFrame(data.columns.tolist(), columns = ['Variable'])
    df_var_validity = pd.DataFrame(var_validity, columns = ['Data since'])
    df_var_descr = pd.concat([df_cols, df_var_descr, df_var_validity], axis = 1)
    df_var_descr.set_index('Variable', inplace = True)
    df_var_descr


def _filter_data_by_date(data):
    date_min = datetime.date(data.index.min().year, data.index.min().month, data.index.min().day)
    today = datetime.datetime.today().date()

    dt = np.round(data.index.diff().mean().total_seconds()/60, 0)

    if dt > 10.0:
        d = st.date_input(
            "Select time range",
            (today - datetime.timedelta(days = 30), today),
            min_value=date_min,
            max_value=today,
            format="YYYY-MM-DD",
        )
    else:
        d = st.date_input(
            "Select time range",
            (today - datetime.timedelta(days = 1), today),
            min_value=date_min,
            max_value=today,
            format="YYYY-MM-DD",
        )        

    #Filtrar datos por período de tiempo
    dt_ini = pd.to_datetime(d[0])
    dt_end = pd.to_datetime(d[1])
    data_filter = data[ (data.index >= dt_ini) & (data.index <= dt_end) ]
    return data_filter, dt_ini, dt_end


def _plot_interactive_historical(data_filter, column):
    if data_filter[column].empty:
        st.write("No data to plot. Check variable availability in the variable description table.")
    else:
        fig = px.line(data_filter, x=data_filter.index, y=f"{column}")
        st.plotly_chart(fig)


def _plot_static_historical(data_filter, column):
    if data_filter[column].empty:
        st.write("No data to plot. Check variable availability in the variable description table.")
    else:
        fig, ax = plt.subplots()
        ax.plot(data_filter[column].dropna())
        ax.set_xlabel('date')
        ax.set_ylabel(column)
        ax.grid()
        fig.autofmt_xdate()
        st.pyplot(fig)


def _plot_interactive_histogram(data, column):
    if data[column].empty:
        st.write("No data to plot. Check variable availability in the variable description table.")
    else:
        if column == 'pcp (mm)' or column == 'daily_rain_mm':
            data = data[ data[column] >= 1. ] 
        fig = px.histogram(data[column].dropna(), x=f"{column}", nbins = 30)
        st.plotly_chart(fig)


def _plot_static_histogram(data, column):
    if data[column].empty:
        st.write("No data to plot. Check variable availability in the variable description table.")
    else:
        if column == 'pcp (mm)' or column == 'daily_rain_mm':
            data = data[ data[column] >= 1. ]
        fig, ax = plt.subplots()
        ax.hist(data[column].dropna(), bins=30, edgecolor='k')
        ax.set_xlabel(column)
        ax.set_ylabel('Frequency')
        ax.grid()
        st.pyplot(fig)


def _plot_daily_annual_comp_temp(daily_data):
    daily_data = daily_data.reset_index()
    year_min = 2021
    max_year = daily_data.date.max().year
    years = np.arange(year_min, max_year + 1, 1)
    fig, axs = plt.subplots(nrows = 3, ncols = 1, figsize = (12,16))
    plt.suptitle('Estación meteorológica Secar de la Real (Palma, España) \n Datos diarios. Elevación: 75 m \n', fontsize = 16, fontweight = 'bold')

    # dates = daily_data[daily_data['date'].dt.year == 2022]['date'].dt.strftime('%m-%d')

    for year in years:
        daily_data_year = daily_data[daily_data['date'].dt.year == year]
        daily_data_year.loc[:, 'date'] = daily_data_year['date'].dt.strftime('%m-%d')
        # daily_data_year.set_index('date', inplace = True)
        
        daily_data_year.plot('date', 'high_temp_deg', ax = axs[0], label = year)
        daily_data_year.plot('date', 'low_temp_deg', ax = axs[1], label = year)
        daily_data_year.plot('date', 'temp_out_deg', ax = axs[2], label = year)    

    axs[0].set_title('Temperatura máxima diaria', fontsize = 12)
    axs[0].set_title(f'Validez datos de temperatura: 2021-{str(max_year)}', fontsize = 9, loc = 'right')        
    axs[0].set_ylabel('T (°C)')
    # axs[0].set_xlim([dates.min(), dates.max()])

    axs[1].set_title('Temperatura mínima diaria', fontsize = 12)
    axs[1].set_ylabel('T (°C)')
    # axs[1].set_xlim([dates.min(), dates.max()])

    axs[2].set_title('Temperatura media diaria', fontsize = 12)
    axs[2].set_ylabel('T (°C)')
    # axs[2].set_xlim([dates.min(), dates.max()])

    for ax in axs:
        ax.grid()
        # set monthly locator
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        # set formatter
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))

        ax.margins(x = 0.0)

    plt.tight_layout()
    st.pyplot(fig)


def _plot_daily_annual_comp_pcp(daily_data):
    daily_data = daily_data.reset_index()
    year_min = daily_data.date.min().year
    max_year = daily_data.date.max().year
    years = np.arange(year_min, max_year + 1, 1)
    fig, axs = plt.subplots(nrows = 2, ncols = 1, figsize = (16,12))
    plt.suptitle('Estación meteorológica Secar de la Real (Palma, España) \n Datos diarios. Elevación: 75 m \n', fontsize = 16, fontweight = 'bold')

    for year in years:
        daily_data_year = daily_data[daily_data['date'].dt.year == year]
        daily_data_year = daily_data_year.copy()
        daily_data_year.loc[:, 'pcp_acum_mm'] = daily_data_year['pcp (mm)'].cumsum()
        daily_data_year.loc[:, 'date'] = daily_data_year['date'].dt.strftime('%m-%d')
        # daily_data_year.set_index('date', inplace = True)
        
        daily_data_year.plot('date', 'pcp (mm)', ax = axs[0], legend = True, label = year)    
        daily_data_year.plot('date', 'pcp_acum_mm', ax = axs[1], legend = True, label = year)    

    #plot accumulated pcp daily mean sum
    pcp_mean_daily_cumsum = daily_data['pcp (mm)'].groupby(daily_data['date'].dt.strftime('%m-%d')).mean().cumsum()
    axs[1].plot(pcp_mean_daily_cumsum.index, pcp_mean_daily_cumsum, c = 'black', lw = 3, label = 'Media')

    axs[0].set_title('Precipitación diaria', fontsize = 12)
    axs[0].set_title(f'Validez datos de precipitación: 2014-{str(max_year)}', fontsize = 9, loc = 'right')            
    axs[0].set_ylabel('Prec. (mm)')

    axs[1].set_title('Precipitación acumulada', fontsize = 12)
    axs[1].set_title(f'Validez datos de precipitación: 2014-{str(max_year)}', fontsize = 9, loc = 'right')            
    axs[1].set_ylabel('Prec. (mm)')
    axs[1].legend()

    plt.gca().set_ylim(bottom=0)

    for ax in axs:
        ax.grid()
        # set monthly locator
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        # # set formatter
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    
        ax.margins(x = 0.0)

    plt.tight_layout()
    st.pyplot(fig)


def _plot_sensor_comparison_daily_data_pcp_current_year(daily_data):
    daily_data.reset_index(inplace = True)
    max_year = daily_data.date.max().year
    fig, axs = plt.subplots(nrows = 1, ncols = 1, figsize = (12,8))
    plt.suptitle('Estación meteorológica Secar de la Real (Palma, España) \n Datos diarios. Elevación: 75 m \n', fontsize = 16, fontweight = 'bold')

    daily_data_year = daily_data[daily_data['date'].dt.year == max_year]
    daily_data_year = daily_data_year.copy()
    daily_data_year.loc[:, 'pcp_acum_man_mm'] = daily_data_year['pcp (mm)'].cumsum()
    daily_data_year.loc[:, 'pcp_acum_pws_mm'] = daily_data_year['daily_rain_mm'].cumsum()

    daily_data_year.loc[:, 'date'] = daily_data_year['date'].dt.strftime('%m-%d')
    # daily_data_year.set_index('date', inplace = True)
    
    axs.set_title(f"Pluvio manual: {np.round(daily_data_year.pcp_acum_man_mm.max(), 1)} mm", loc = 'left', fontsize = 10, fontweight = 'bold')
    axs.set_title(f"Pluvio Vantage Vue: {np.round(daily_data_year.pcp_acum_pws_mm.max(), 1)} mm", loc = 'right', fontsize = 10, fontweight = 'bold')

    daily_data_year.plot('date', 'pcp_acum_man_mm', ax= axs, legend = True, color = 'blue', label = f"Pluviómetro manual {max_year}")    
    daily_data_year.plot('date', 'pcp_acum_pws_mm', ax= axs, legend = True, color = 'darkturquoise', label = f"Pluviómetro Davis Vantage Vue {max_year}")    
    #plot accumulated pcp daily mean sum
    pcp_mean_daily_cumsum = daily_data['pcp (mm)'].groupby(daily_data['date'].dt.strftime('%m-%d')).mean().cumsum()
    axs.plot(pcp_mean_daily_cumsum.index, pcp_mean_daily_cumsum, c = 'black', lw = 3, label = f'Media 2014-{max_year}')

    axs.set_title('Precipitación diaria acumulada', fontsize = 12)
    axs.set_title(f'Validez datos de precipitación pluvio manual: 2014-{str(max_year)} \n Validez datos de precipitación Vantage Vue: 2021-{str(max_year)}', fontsize = 9)            
    axs.set_ylabel('Prec. (mm)')

    plt.gca().set_ylim(bottom=0)

    axs.grid()
    axs.legend()
    # set monthly locator
    axs.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    # # set formatter
    axs.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    
    axs.margins(x = 0.0)

    plt.tight_layout()
    st.pyplot(fig)


def _plot_monthly_data_temp(monthly_data, monthly_data_means):
    year_min = 2021
    max_year = monthly_data.date.max().year
    years = np.arange(year_min, max_year + 1, 1)
    fig, axs = plt.subplots(nrows = 3, ncols = 1, figsize = (12,16))
    fig.suptitle('Estación meteorológica Secar de la Real (Palma, España) \n Datos mensuales. Elevación: 75 m \n', fontsize = 16, fontweight = 'bold')
    for year in years:
        monthly_data_year = monthly_data[monthly_data['date'].dt.year == year]
        monthly_data_year = monthly_data_year.copy()
        monthly_data_year.loc[:, 'date'] = monthly_data_year['date'].dt.strftime('%m')
        # daily_data_year.set_index('date', inplace = True)
        axs[0].plot(monthly_data_year['date'], monthly_data_year['mean_high_temp_deg'], label = year)
        axs[1].plot(monthly_data_year['date'], monthly_data_year['mean_low_temp_deg'], label = year)
        axs[2].plot(monthly_data_year['date'], monthly_data_year['mean_temp_out_deg'], label = year)
    axs[0].plot(monthly_data_means.index, monthly_data_means['mean_high_temp_deg'], c = 'black', lw = 3, label = f'Media')
    axs[1].plot(monthly_data_means.index, monthly_data_means['mean_low_temp_deg'], c = 'black', lw = 3, label = f'Media')
    axs[2].plot(monthly_data_means.index, monthly_data_means['mean_temp_out_deg'], c = 'black', lw = 3, label = f'Media')
    
    # dateticks_format = DateFormatter('%b')

    axs[0].set_title('Temperatura máxima media mensual', fontsize = 12)
    axs[0].set_title(f'Validez datos de temperatura: 2021-{str(max_year)}', fontsize = 9, loc = 'right')    
    axs[0].set_ylabel('T (°C)')
    axs[0].set_xlabel('Mes del año')
    axs[0].set_xlim([monthly_data_means.index.min(), monthly_data_means.index.max()])
    axs[0].grid()
    axs[0].legend()

    axs[1].set_title('Temperatura mínima media mensual', fontsize = 12)
    axs[1].set_ylabel('T (°C)')
    axs[1].set_xlabel('Mes del año')
    axs[1].set_xlim([monthly_data_means.index.min(), monthly_data_means.index.max()])
    axs[1].grid()
    axs[1].legend()

    axs[2].set_title('Temperatura media mensual', fontsize = 12)
    axs[2].set_ylabel('T (°C)')
    axs[2].set_xlabel('Mes del año')
    axs[2].set_xlim([monthly_data_means.index.min(), monthly_data_means.index.max()])
    axs[2].grid()
    axs[2].legend()
    
    plt.tight_layout()
    st.pyplot(fig)


def _plot_monthly_yearly_data_pcp(monthly_data, monthly_data_means):
    year_min = monthly_data.date.min().year
    max_year = monthly_data.date.max().year
    years = np.arange(year_min, max_year + 1, 1)
    fig, axs = plt.subplots(nrows = 2, ncols = 1, figsize = (16,12))
    fig.suptitle('Estación meteorológica Secar de la Real (Palma, España) \n Datos mensuales. Elevación: 75 m \n', fontsize = 16, fontweight = 'bold')
    for year in years:
        monthly_data_year = monthly_data[monthly_data['date'].dt.year == year]
        monthly_data_year['date'] = monthly_data_year['date'].dt.strftime('%m')
        # daily_data_year.set_index('date', inplace = True)
        axs[0].plot(monthly_data_year['date'], monthly_data_year['pcp_acum_month_mm'], label = year)
    axs[0].plot(monthly_data_means.index, monthly_data_means['mean_pcp_acum_month_mm'], c = 'black', lw = 3, label = f'Media')
    bar = axs[1].bar(years, monthly_data.set_index('date').resample('Y').sum()['pcp_acum_month_mm'], color = 'blue')
    axs[1].bar_label(bar)
    # dateticks_format = DateFormatter('%b')

    axs[0].set_title('Precipitación mensual', fontsize = 12)
    axs[0].set_title(f'Validez datos de precipitación: 2014-{str(max_year)}', fontsize = 9, loc = 'right')        
    axs[0].set_ylabel('Prec. (mm)')
    axs[0].set_xlabel('Mes del año')
    axs[0].set_xlim([monthly_data_means.index.min(), monthly_data_means.index.max()])
    axs[0].grid()
    axs[0].legend()

    axs[1].set_title('Precipitación anual', fontsize = 12)
    axs[1].set_title(f'Validez datos de precipitación: 2014-{str(max_year)}', fontsize = 9, loc = 'right')        
    axs[1].set_ylabel('Prec. (mm)')
    axs[1].set_xlabel('Año')
    axs[1].set_xticks(years)
    axs[1].grid()
    
    plt.tight_layout()
    st.pyplot(fig)


def _get_extreme_data(data):
    max_vals = pd.DataFrame(data.max().round(1), columns = ['max_value'])
    date_max_vals = pd.DataFrame(data.idxmax().dt.date, columns = ['date_max_value'])
    max_vals = pd.concat([max_vals, date_max_vals], axis = 1)#.rename(columns = {'index': 'variable'}).set_index('variable')

    min_vals = pd.DataFrame(data.min().round(1), columns = ['min_value'])
    date_min_vals = pd.DataFrame(data.idxmin().dt.date, columns = ['date_min_value'])
    min_vals = pd.concat([min_vals, date_min_vals], axis = 1)#.rename(columns = {'index': 'variable'}).set_index('variable')

    extr_vals = pd.concat([min_vals, max_vals], axis = 1)
    return(extr_vals)

# 1st order functions

def homepage():
    # Título de la aplicación
    st.title("Palma Secar de la Real weather data")

    st.write("In this web app you can find my weather station data\
            located in Palma Secar de la Real neighborhood, Mallorca")

    st.markdown("## Station location")
    map_data = _get_map_data()
    st.map(map_data)


def current_conditions_page():

    st.markdown("## Current conditions")
    st.write("Data taken from Wunderground web API. Update interval: 20 seconds")

    while True:
        current_data = _get_current_weather_data(mode = 'current')  
        placeholder = st.empty()
        with placeholder.container():
            _show_current_weather_data(current_data)
        time.sleep(20)
        placeholder.empty()


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


def recent_data_page():

    st.markdown("# Recent data")
    st.sidebar.header("Recent data")
    st.write(
        """In this page you can inspect weather data of the last 30 days."""
    )

    data = _load_daily_data()
    data_current = _filter_current_data(data)
    column = _select_column_box(data, key = "pcp (mm)")

    _plot_interactive_current(data_current, column)
    _plot_static_current(data_current, column)

    #Añadir descripción de variables
    st.write("Variable description")
    _get_df_variable_description(data)


def annual_comparison_page():

    st.markdown("# Annual data comparison")
    st.write("In this page you can find daily data comparisons between different years")

    st.text("Please note that there are 2 precipitation series: one with manual \n \
        records and the other with data from the automatic weather station. \n \
        The plotted data showed here are the precipitation from manual rain gauge.")

    st.markdown("## Daily Temperature")

    daily_data = _load_daily_data()
    _plot_daily_annual_comp_temp(daily_data)
    monthly_data = _get_monthly_data(daily_data)
    monthly_data_means = _get_monthly_data_means(monthly_data)

    st.markdown("## Daily Precipitation")
    _plot_daily_annual_comp_pcp(daily_data)
    _plot_sensor_comparison_daily_data_pcp_current_year(daily_data)

    st.markdown("## Monthly Temperature")
    _plot_monthly_data_temp(monthly_data, monthly_data_means)

    st.markdown("## Monthly and yearly Precipitation")
    _plot_monthly_yearly_data_pcp(monthly_data, monthly_data_means)


def historical_data_page():

    st.markdown("# Historical data")
    st.sidebar.header("Historical data")
    st.write(
        """In this page you can inspect historical weather data"""
    )

    #Crear gráfico de una variable del dataset para el período seleccionado
    st.markdown('## Time series data')

    st.write("Select type of data")      

    #Seleccionar un período de tiempo y representar período de tiempo
    data = _select_history_data_type(key = "Daily data")
    # data = _load_daily_data()
    st.write("Select a time period")      

    data_filter, dt_ini, dt_end = _filter_data_by_date(data)
    data_filter = data_filter.round(1)

    # Seleccionar una variable del dataset
    column = _select_column_box(data, key = "temp_out_deg") # key parameter is used to prevent errors when displaying 

    st.write(f"Interactive daily evolution plot for {column}.\
            Period from {dt_ini.strftime('%d-%m-%Y')} to {dt_end.strftime('%d-%m-%Y')}")
    _plot_interactive_historical(data_filter, column)

    st.write(f"Static daily evolution plot for {column}.\
            Period from {dt_ini.strftime('%d-%m-%Y')} to {dt_end.strftime('%d-%m-%Y')}")
    _plot_static_historical(data_filter, column)

    #Mostrar datos en forma de tabla
    st.write("Data in table format for the selected period")
    
    # column-cmap mapping
    cmaps = {'pcp (mm)': 'Blues', 'high_temp_deg': 'jet',
             'wind_gust_kmh': 'Greys', 'rain_10min_mm': 'Blues',
             'rain_rate_mmh': 'Blues', 'low_temp_deg': 'jet',
             'daily_rain_mm': 'Blues', 'temp_out_deg': 'jet',
             'rel_humidity_perc': 'BuPu', 'dewpoint_deg': 'BuPu',
             'wind_speed_kmh': 'Greys', 'pressure_hPa': 'PuRd'}
    # default gradient
    style = data_filter.style.background_gradient()
    for col, cmap in cmaps.items():
        style = style.background_gradient(cmap, subset=col)
    
    # st.data_editor(data_filter, column_config={"high_temp_deg": st.column_config.NumberColumn("Daily maximum temperature", format = "%.1f")})
    st.dataframe(style)
    #Añadir descripción de variables
    st.write("Variable description")
    _get_df_variable_description(data)


def statistics_page():

    st.markdown("# Station statistics")
    st.sidebar.header("Statistics")
    st.write(
        """In this page you can inspect the station data statistics"""
    ) 

    #Seleccionar un período de tiempo y representar período de tiempo
    data = _load_daily_data()
    raw_data = _load_10min_data()

    #Crear rosa de los vientos con datos 10-minutales
    st.markdown("## Wind rose")
    st.write("Wind rose for 10-min average wind speed")

    wind_data = _get_wind_data(raw_data)
    wind_rose_data = _get_df_wind_rose(wind_data)
    _plot_interactive_wind_rose(wind_rose_data)


    # Crear el histograma
    st.markdown('## Histogram')
    st.write("Plot a histogram for a variable. Uses all available data")
    # Seleccionar una variable del dataset
    column = _select_column_box(data, key = "high_temp_deg")

    st.write(f"Interactive histogram of {column}. {len(data[column].dropna())} values were used.")
    _plot_interactive_histogram(data, column)

    st.write(f"Static histogram of {column}. {len(data[column].dropna())} values were used.")
    _plot_static_histogram(data, column)

    #Añadir descripción de variables
    st.write("Variable description")
    _get_df_variable_description(data)



def extreme_data_page():
    
    st.markdown("# Extreme data")
    st.sidebar.header("Extreme data")
    st.write(
        """In this page you can inspect extreme data from the weather
        station"""
    )

    # Cargar el dataset desde un archivo local
    data = _load_daily_data()

    #Calculate extreme weather data
    extr_data = _get_extreme_data(data)

    st.dataframe(extr_data)


# Create pages and sidebar
page_names_to_funcs = {
    "Home": homepage,
    "Current conditions": current_conditions_page,
    "Daily summary": daily_summary_page,
    "Recent data": recent_data_page,
    "Annual data comparison": annual_comparison_page,
    "Historical data": historical_data_page,
    "Statistics": statistics_page,
    "Data extremes": extreme_data_page
}

demo_name = st.sidebar.selectbox("Choose a page", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()