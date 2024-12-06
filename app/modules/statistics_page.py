import streamlit as st
from historical_data_page import _load_10min_data, _load_daily_data
import numpy as np
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
from daily_summary_page import _select_column_box
from recent_data_page import _get_df_variable_description


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