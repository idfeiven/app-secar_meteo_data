import os
import pandas as pd
import streamlit as st
from daily_summary_page import _plot_interactive_current, _plot_static_current, _select_column_box
from datetime import datetime

# Cargar el dataset desde un archivo local
@st.cache_data
def _load_daily_data():
    fpath = "secar_daily_data.xlsx"
    daily_data = pd.read_excel(fpath)
    daily_data = daily_data.drop('Unnamed: 0', axis = 1)
    daily_data.set_index('date', inplace = True)
    return daily_data


def _filter_current_data(data):
    data_current = data[data.index.year == datetime.datetime.now().year]
    return data_current


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