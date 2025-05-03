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

#----------------------------------FUNCTIONS----------------------------------#

def select_history_data_type(key = "Daily data"):
    #Seleccionar el tipo de datos históricos a representar
    data_type = st.selectbox("Selecciona el tipo de datos a representar", ["10-min data", "Daily data"], key = key)
    if data_type == "Daily data":
        daily_data = load_daily_data()
        daily_data.rename(columns = get_dict_rename_cols(), inplace=True)
        return daily_data, data_type
    
    elif data_type == "10-min data":
        raw_data = load_10min_data()
        raw_data['pcp (mm)'] = np.nan
        raw_data['daily_rain_mm'] = np.nan
        raw_data.rename(columns = get_dict_rename_cols(), inplace=True)
        return raw_data, data_type


def filter_data_by_date(data):
    date_min = datetime.date(data.index.min().year, data.index.min().month, data.index.min().day)
    today = datetime.datetime.today().date()

    dt = np.round(data.index.diff().mean().total_seconds()/60, 0)

    if dt > 10.0:
        d = st.date_input(
            "Seleccionar rango de tiempo",
            (today - datetime.timedelta(days = 30), today),
            min_value=date_min,
            max_value=today,
            format="YYYY-MM-DD",
        )
    else:
        d = st.date_input(
            "Seleccionar rango de tiempo",
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
        st.write("No hay datos para el período seleccionado")
    else:
        fig = px.line(data_filter, x=data_filter.index, y=f"{column}")
        st.plotly_chart(fig)

#----------------------------------MAIN----------------------------------#

st.markdown("# Datos históricos")
st.write(
    """En esta página puedes inspeccionar datos históricos del clima"""
)

# Crear gráfico de una variable del dataset para el período seleccionado
st.markdown('## Datos de series temporales')

st.write("Selecciona el tipo de datos")      

#Seleccionar un período de tiempo y representar período de tiempo
data, data_type = select_history_data_type(key = "Daily data")
# data = _load_daily_data()
st.write("Selecciona el período de tiempo para representar los datos")      

data_filter, dt_ini, dt_end = filter_data_by_date(data)
# data_filter = data_filter.round(1)

# Seleccionar una variable del dataset
column = select_column_box(data, key = data.columns[0]) # key parameter is used to prevent errors when displaying 

st.write(f"Evolución de datos para {column}.\
        Período desde {dt_ini.strftime('%d-%m-%Y')} hasta {dt_end.strftime('%d-%m-%Y')}")
plot_interactive_historical(data_filter, column)

#Mostrar datos en forma de tabla
st.write("Datos en forma de tabla")

# column-cmap mapping
cmaps_daily = {'Precipitación diaria (pluviómetro manual, mm)': 'Blues',
    'Temperatura máxima (°C)': 'jet',
    'Ráfaga de viento (km/h)': 'Greys',
    'Precipitación en 10 minutos (mm)': 'Blues',
    'Tasa de lluvia instantánea (mm/h)': 'Blues',
    'Temperatura mínima (°C)': 'jet',
    'Precipitación diaria (estación meteorológica, mm)': 'Blues',
    'Temperatura (°C)': 'jet',
    'Humedad media (%)': 'BuPu',
    'Humedad máxima (%)': 'BuPu',
    'Humedad mínima (%)': 'BuPu',
    'Punto de rocío (°C)': 'BuPu',
    'Velocidad del viento (km/h)': 'Greys',
    'Presión media al nivel del mar (hPa)': 'PuRd',
    'Presión máxima al nivel del mar (hPa)': 'PuRd',
    'Presión mínima al nivel del mar (hPa)': 'PuRd'}

cmaps_10min = {
    'Temperatura máxima (°C)': 'jet',
    'Ráfaga de viento (km/h)': 'Greys',
    'Precipitación en 10 minutos (mm)': 'Blues',
    'Tasa de lluvia instantánea (mm/h)': 'Blues',
    'Temperatura mínima (°C)': 'jet',
    'Temperatura (°C)': 'jet',
    'Humedad (%)': 'BuPu',
    'Punto de rocío (°C)': 'BuPu',
    'Velocidad del viento (km/h)': 'Greys',
    'Presión al nivel del mar (hPa)': 'PuRd'}

# default gradient
style = data_filter.style.background_gradient()

if data_type == "Daily data":
    cmaps = cmaps_daily
if data_type == "10-min data":
    cmaps = cmaps_10min

for col, cmap in cmaps.items():
    style = style.background_gradient(cmap, subset=col)

st.dataframe(style)