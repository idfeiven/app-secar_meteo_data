# common functions to use in the app modules

import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go


def select_column_box(data, key):
    # Seleccionar una variable del dataset
    column = st.selectbox("Select a variable to plot", data.columns, key = key)
    return column


def get_dict_rename_cols():

    dict_rename_cols = {"pcp (mm)": "Daily Precipitation (manual rain gauge, mm)",
                      "high_temp_deg": "Maximum Temperature (°C)",
                      "wind_gust_kmh": "Wind Gust (km/h)",
                      "wind_gust_dir": "Wind Gust Direction (°)",
                      "rain_10min_mm": "Precipitation in 10 minutes (mm)",
                      "rain_rate_mmh": "Instantaneous Rain Rate (mm/h)",
                      "low_temp_deg": "Minimum Temperature (°C)",
                      "daily_rain_mm": "Daily precipitation (weather station, mm)",
                      "temp_out_deg": "Temperature (°C)",
                      "rel_humidity_perc": "Humidity (%)",
                      "mean_rel_humidity_perc": "Mean Humidity (%)",
                      "max_rel_humidity_perc": "Maximum Humidity (%)",
                      "min_rel_humidity_perc": "Minimum Humidity (%)",
                      "dewpoint_deg": "Dew Point (°C)",
                      "wind_speed_kmh": "Wind Speed (km/h)",
                      "wind_direction": "Wind Direction (°)",
                      "pressure_hPa": "Sea Level Pressure (hPa)",
                      "mean_pressure_hPa": "Mean Sea Level Pressure (hPa)",
                      "max_pressure_hPa": "Maximum Sea Level Pressure (hPa)",
                      "min_pressure_hPa": "Minimum Sea Level Pressure (hPa)"}

    return dict_rename_cols


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


def plot_interactive_data_by_year(df, value_col, title, yaxis_title):

    fig = go.Figure()
    
    # Añadir columna con fecha ficticia para alineación
    df['aligned_date'] = pd.to_datetime('2000-' + df.index.strftime('%m-%d'))

    for year in sorted(df.dropna(subset=value_col).index.year.unique()):
        yearly_data = df[df.index.year == year]
        fig.add_trace(go.Scatter(
            x=yearly_data['aligned_date'],
            y=yearly_data[value_col],
            mode='lines',
            name=str(year)
        ))

    fig.update_layout(
        title=title,
        xaxis_title='Día del año',
        yaxis_title=yaxis_title,
        xaxis=dict(tickformat='%d-%m'),
        height=500,
        width=900
    )

    return fig


def plot_interactive_comparison_cumulative_data(df,
                                                year,
                                                col_1,
                                                col_2,
                                                col_mean,
                                                title,
                                                yaxis_title):

    fig = go.Figure()
    
    # Añadir columna con fecha ficticia para alineación
    df['aligned_date'] = pd.to_datetime('2000-' + df.index.strftime('%m-%d'))

    cumsum_mean = df[col_mean].groupby(df.index.strftime('%m-%d')).mean().cumsum()
    year_min = df[col_mean].dropna().index.year.min()

    yearly_data = df[df.index.year == year]
    fig.add_trace(go.Scatter(
        x=yearly_data['aligned_date'],
        y=yearly_data[col_1].cumsum(),
        mode='lines',
        name=str(year)
    ))

    fig.add_trace(go.Scatter(
    x=yearly_data['aligned_date'],
    y=yearly_data[col_2].cumsum(),
    mode='lines',
    name=str(year)
    ))

    fig.add_trace(go.Scatter(
    x=yearly_data['aligned_date'],
    y=cumsum_mean,
    mode='lines',
    name=f"Media {year_min}-{year}"
    ))

    fig.update_layout(
        title=title,
        xaxis_title='Día del año',
        yaxis_title=yaxis_title,
        xaxis=dict(tickformat='%d-%m'),
        height=500,
        width=900
    )

    return fig


def get_monthly_data(daily_data):
    #resample daily data to monthly data:
    max_monthly_data = daily_data.resample('ME').max()\
                        [['high_temp_deg', 'wind_gust_kmh', 'rain_10min_mm', 'rain_rate_mmh']]\
                        .rename(columns = {'high_temp_deg': 'Monthly max. temperature (°C)',
                                           'wind_gust_kmh': 'Monthly max. wind gust (km/h)',
                                           'rain_10min_mm': 'Monthly max. rain in 10 minutes (mm)',
                                           'rain_rate_mmh': 'Monthly max. instantaneous rain rate (mm/h)'})

    min_monthly_data = daily_data.resample('ME').min()[['low_temp_deg']]\
        .rename(columns= {'low_temp_deg': 'Monthly min. temperature (°C)'})

    mean_monthly_data = daily_data\
        .resample('ME').mean()[['temp_out_deg', 'high_temp_deg', 'low_temp_deg' ,'mean_rel_humidity_perc', 'dewpoint_deg', 'wind_speed_kmh', 'mean_pressure_hPa']]\
        .rename(columns={'temp_out_deg': 'Monthly mean temperature (°C)',
                         'high_temp_deg': 'Monthly mean max. temperatures (°C)',
                         'low_temp_deg': 'Monthly mean min. temperatures (°C)',
                         'mean_rel_humidity_perc': 'Monthly mean relative humidity (%)',
                         'dewpoint_deg': 'Monthly mean dewpoint (°C)',
                         'wind_speed_kmh': 'Monthly mean wind speed (km/h)',
                         'mean_pressure_hPa': 'Monthly mean pressure (hPa)'})

    monthly_pcp_data = daily_data.resample('ME').sum()[['pcp (mm)']]
    #group all monthly data
    monthly_data = pd.concat([max_monthly_data, min_monthly_data, mean_monthly_data, monthly_pcp_data], axis = 1).rename(columns = {'pcp (mm)': 'Monthly precipitation (mm)'})
    monthly_data = monthly_data.reset_index()  
    return(monthly_data) 