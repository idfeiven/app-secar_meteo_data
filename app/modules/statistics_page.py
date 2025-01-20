import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
from common import load_10min_data,\
                   load_daily_data,\
                   select_column_box,\
                   get_dict_rename_cols


def get_wind_data(raw_data):
    wind_data = raw_data[raw_data["wind_speed_kmh"] > 0.0][["wind_speed_kmh", "wind_direction"]]
    wind_data["wind_direction"] = pd.Categorical(wind_data["wind_direction"], ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"])
    wind_data.sort_values("wind_direction", inplace=True)

    return wind_data

def get_df_wind_rose(wind_data):
    bins = np.arange(0.0, wind_data.wind_speed_kmh.max() + 5, 5)
    wind_data['10-min average wind speed (km/h)'] = pd.cut(wind_data['wind_speed_kmh'], bins)
    wind_rose = wind_data.groupby(["10-min average wind speed (km/h)", "wind_direction"]).count().reset_index()
    wind_rose["frequency"] = wind_rose["wind_speed_kmh"]/len(wind_data)

    return wind_rose

def plot_interactive_wind_rose(wind_rose):

    fig = px.bar_polar(wind_rose, r = "frequency", theta="wind_direction",
                   color="10-min average wind speed (km/h)", template="plotly_dark",
                   color_discrete_sequence= px.colors.sequential.Viridis,
                   width = 1200,
                   height = 1000)
    
    st.plotly_chart(fig)


def plot_interactive_histogram(data, column):
    if data[column].empty:
        st.write("No data to plot. Check variable availability in the variable description table.")
    else:
        if column == 'pcp (mm)' or column == 'daily_rain_mm':
            data = data[ data[column] >= 1. ] 
        fig = px.histogram(data[column].dropna(), x=f"{column}", nbins = 30)
        st.plotly_chart(fig)


def plot_static_histogram(data, column):
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


st.markdown("# Station statistics")
st.write(
    """In this page you can inspect the station data statistics"""
) 

#Seleccionar un período de tiempo y representar período de tiempo
data = load_daily_data()
raw_data = load_10min_data()

#Crear rosa de los vientos con datos 10-minutales
st.markdown("## Wind rose")
st.write("Wind rose for 10-min average wind speed")

wind_data = get_wind_data(raw_data)
wind_rose_data = get_df_wind_rose(wind_data)
plot_interactive_wind_rose(wind_rose_data)


# Crear el histograma
st.markdown('## Histogram')
st.write("Plot a histogram for a variable. Uses all available data")
# Seleccionar una variable del dataset
data.rename(columns = get_dict_rename_cols(), inplace=True)
column = select_column_box(data, key = data.columns[0])

st.write(f"Interactive histogram of {column}. {len(data[column].dropna())} values were used.")
plot_interactive_histogram(data, column)

st.write(f"Static histogram of {column}. {len(data[column].dropna())} values were used.")
plot_static_histogram(data, column)

#Añadir descripción de variables
# st.write("Variable description")
# df_var_descr = get_df_variable_description(data)
# df_var_descr