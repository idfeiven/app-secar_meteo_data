import pandas as pd
import streamlit as st
from common import load_daily_data


def get_extreme_data(data):
    max_vals = pd.DataFrame(data.max().round(1), columns = ['max_value'])
    date_max_vals = pd.DataFrame(data.idxmax().dt.date, columns = ['date_max_value'])
    max_vals = pd.concat([max_vals, date_max_vals], axis = 1)#.rename(columns = {'index': 'variable'}).set_index('variable')

    min_vals = pd.DataFrame(data.min().round(1), columns = ['min_value'])
    date_min_vals = pd.DataFrame(data.idxmin().dt.date, columns = ['date_min_value'])
    min_vals = pd.concat([min_vals, date_min_vals], axis = 1)#.rename(columns = {'index': 'variable'}).set_index('variable')

    extr_vals = pd.concat([min_vals, max_vals], axis = 1)
    extr_vals.rename({"pcp (mm)": "Daily Precipitation (manual rain gauge, mm)",
                      "high_temp_deg": "Maximum Temperature (°C)",
                      "wind_gust_kmh": "Wind Gust (km/h)",
                      "rain_10min_mm": "Precipitation in 10 minutes (mm)",
                      "rain_rate_mmh": "Instantaneous Rain Rate (mm/h)",
                      "low_temp_deg": "Minimum Temperature (°C)",
                      "daily_rain_mm": "Daily precipitation (weather station, mm)",
                      "temp_out_deg": "Daily Mean Temperature (°C)",
                      "rel_humidity_perc": "Daily Mean Humidity (%)",
                      "dewpoint_deg": "Dew Point (°C)",
                      "wind_speed_kmh": "Daily Mean Wind Speed (km/h)",
                      "pressure_hPa": "Mean Sea Level Pressure (hPa)"}, inplace=True)
    
    extr_vals.rename(columns = {"min_value": "Record Minimum",
                      "date_min_value": "Date Record Minimum",
                      "max_value": "Record Maximum",
                      "date_max_value": "Date Record Max"}, inplace=True)
    return(extr_vals)

  
st.markdown("# Extreme data")
st.write(
    """In this page you can inspect extreme data from the weather
    station"""
)

# Cargar el dataset desde un archivo local
data = load_daily_data()

#Calculate extreme weather data
extr_data = get_extreme_data(data)

st.dataframe(extr_data)