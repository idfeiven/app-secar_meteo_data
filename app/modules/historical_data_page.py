import datetime
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
from common import load_10min_data,\
                   load_daily_data,\
                   select_column_box,\
                   get_dict_rename_cols\


def select_history_data_type(key = "Daily data"):
    #Seleccionar el tipo de datos históricos a representar
    data_type = st.selectbox("Select data type to plot", ["10-min data", "Daily data"], key = key)
    if data_type == "Daily data":
        daily_data = load_daily_data()
        daily_data.rename(columns = get_dict_rename_cols(), inplace=True)
        return daily_data
    elif data_type == "10-min data":
        raw_data = load_10min_data()
        raw_data['pcp (mm)'] = np.nan
        raw_data['daily_rain_mm'] = np.nan
        raw_data.rename(columns = get_dict_rename_cols(), inplace=True)
        return raw_data


def filter_data_by_date(data):
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


def plot_interactive_historical(data_filter, column):
    if data_filter[column].empty:
        st.write("No data to plot. Check variable availability in the variable description table.")
    else:
        fig = px.line(data_filter, x=data_filter.index, y=f"{column}")
        st.plotly_chart(fig)


def plot_static_historical(data_filter, column):
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


st.markdown("# Historical data")
st.write(
    """In this page you can inspect historical weather data"""
)

#Crear gráfico de una variable del dataset para el período seleccionado
st.markdown('## Time series data')

st.write("Select type of data")      

#Seleccionar un período de tiempo y representar período de tiempo
data = select_history_data_type(key = "Daily data")
# data = _load_daily_data()
st.write("Select a time period")      

data_filter, dt_ini, dt_end = filter_data_by_date(data)
# data_filter = data_filter.round(1)

# Seleccionar una variable del dataset
column = select_column_box(data, key = data.columns[0]) # key parameter is used to prevent errors when displaying 

st.write(f"Interactive daily evolution plot for {column}.\
        Period from {dt_ini.strftime('%d-%m-%Y')} to {dt_end.strftime('%d-%m-%Y')}")
plot_interactive_historical(data_filter, column)

st.write(f"Static daily evolution plot for {column}.\
        Period from {dt_ini.strftime('%d-%m-%Y')} to {dt_end.strftime('%d-%m-%Y')}")
plot_static_historical(data_filter, column)

#Mostrar datos en forma de tabla
st.write("Data in table format for the selected period")

# column-cmap mapping
cmaps = {'Daily Precipitation (manual rain gauge, mm)': 'Blues',
        'Maximum Temperature (°C)': 'jet',
        'Wind Gust (km/h)': 'Greys',
        'Precipitation in 10 minutes (mm)': 'Blues',
        'Instantaneous Rain Rate (mm/h)': 'Blues',
        'Minimum Temperature (°C)': 'jet',
        'Daily precipitation (weather station, mm)': 'Blues',
        'Temperature (°C)': 'jet',
        'Humidity (%)': 'BuPu',
        'Dew Point (°C)': 'BuPu',
        'Wind Speed (km/h)': 'Greys',
        'Mean Sea Level Pressure (hPa)': 'PuRd'}
# default gradient
style = data_filter.style.background_gradient()
for col, cmap in cmaps.items():
    style = style.background_gradient(cmap, subset=col)

# st.data_editor(data_filter, column_config={"high_temp_deg": st.column_config.NumberColumn("Daily maximum temperature", format = "%.1f")})
st.dataframe(style)
#Añadir descripción de variables
# st.write("Variable description")
# df_var_descr = get_df_variable_description(data)
# df_var_descr