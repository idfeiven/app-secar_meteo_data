# common functions to use in the app modules

import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

def select_column_box(data, key):
    # Seleccionar una variable del dataset
    column = st.selectbox("Select a variable to plot", data.columns, key = key)
    return column


def get_df_variable_description(data):
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
    return df_var_descr


# Cargar el dataset desde un archivo local
@st.cache_data
def load_daily_data():
    parent_dir = Path(__file__).parent
    data_dir = parent_dir.parent.parent / "data" / "secar_daily_data.xlsx"
    daily_data = pd.read_excel(data_dir)
    daily_data = daily_data.drop('Unnamed: 0', axis = 1)
    daily_data.set_index('date', inplace = True)
    return daily_data


@st.cache_data
def load_10min_data():
    parent_dir = Path(__file__).parent
    data_dir = parent_dir.parent.parent / "data" / "secar_10min_data.xlsx"

    daily_data = pd.read_excel(data_dir)
    daily_data = daily_data.drop('Unnamed: 0', axis = 1)
    daily_data.set_index('date', inplace = True)
    return daily_data


def plot_interactive_current(data_current, column):
    #Crear gráfico de una variable del dataset para el año 2024
    st.write(f"Interactive daily evolution plot for {column}")
    fig = px.line(data_current, x=data_current.index, y=f"{column}")
    st.plotly_chart(fig)


def plot_static_current(data_current, column):
    st.write(f"Static daily evolution plot for {column}")

    fig, ax = plt.subplots()
    ax.plot(data_current[column].dropna())
    ax.set_xlabel('date')
    ax.set_ylabel(column)
    ax.grid()
    fig.autofmt_xdate()
    st.pyplot(fig)