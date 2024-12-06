import streamlit as st
from recent_data_page import _load_daily_data
from daily_summary_page import _select_column_box
from recent_data_page import _get_df_variable_description
import os 
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.express as px


@st.cache_data
def _load_10min_data():
    fpath = 'secar_10min_data.xlsx'
    daily_data = pd.read_excel(fpath)
    daily_data = daily_data.drop('Unnamed: 0', axis = 1)
    daily_data.set_index('date', inplace = True)
    return daily_data


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