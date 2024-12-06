import streamlit as st
from historical_data_page import _load_daily_data
import pandas as pd


def _get_extreme_data(data):
    max_vals = pd.DataFrame(data.max().round(1), columns = ['max_value'])
    date_max_vals = pd.DataFrame(data.idxmax().dt.date, columns = ['date_max_value'])
    max_vals = pd.concat([max_vals, date_max_vals], axis = 1)#.rename(columns = {'index': 'variable'}).set_index('variable')

    min_vals = pd.DataFrame(data.min().round(1), columns = ['min_value'])
    date_min_vals = pd.DataFrame(data.idxmin().dt.date, columns = ['date_min_value'])
    min_vals = pd.concat([min_vals, date_min_vals], axis = 1)#.rename(columns = {'index': 'variable'}).set_index('variable')

    extr_vals = pd.concat([min_vals, max_vals], axis = 1)
    return(extr_vals)


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