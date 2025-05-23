# common functions to use in the app modules

import pandas as pd
import streamlit as st
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go


def select_column_box(data, key):
    # Seleccionar una variable del dataset
    column = st.selectbox("Selecciona una variable para representar", data.columns, key = key)
    return column


def get_dict_rename_cols():

    dict_rename_cols = {"pcp (mm)": "Precipitación diaria (pluviómetro manual, mm)",
                      "high_temp_deg": "Temperatura máxima (°C)",
                      "wind_gust_kmh": "Ráfaga de viento (km/h)",
                      "wind_gust_dir": "Dirección de ráfaga de viento (°)",
                      "rain_10min_mm": "Precipitación en 10 minutos (mm)",
                      "rain_rate_mmh": "Tasa de lluvia instantánea (mm/h)",
                      "low_temp_deg": "Temperatura mínima (°C)",
                      "daily_rain_mm": "Precipitación diaria (estación meteorológica, mm)",
                      "temp_out_deg": "Temperatura (°C)",
                      "rel_humidity_perc": "Humedad (%)",
                      "mean_rel_humidity_perc": "Humedad media (%)",
                      "max_rel_humidity_perc": "Humedad máxima (%)",
                      "min_rel_humidity_perc": "Humedad mínima (%)",
                      "dewpoint_deg": "Punto de rocío (°C)",
                      "wind_speed_kmh": "Velocidad del viento (km/h)",
                      "wind_direction": "Dirección del viento (°)",
                      "pressure_hPa": "Presión a nivel del mar (hPa)",
                      "mean_pressure_hPa": "Presión media a nivel del mar (hPa)",
                      "max_pressure_hPa": "Presión máxima a nivel del mar (hPa)",
                      "min_pressure_hPa": "Presión mínima a nivel del mar (hPa)"}

    return dict_rename_cols


def get_df_variable_description(data):
    var_description = ["Precipitación diaria acumulada del pluviómetro manual",
                    "Temperatura máxima diaria en grados Celsius",
                    "Ráfaga máxima diaria de viento en km/h",
                    "Acumulación máxima diaria de lluvia en 10 minutos del pluviómetro automático",
                    "Tasa máxima diaria de lluvia del pluviómetro automático",
                    "Temperatura mínima diaria en grados Celsius",
                    "Precipitación diaria acumulada del pluviómetro automático",
                    "Temperatura media diaria en grados Celsius",
                    "Humedad relativa media diaria",
                    "Punto de rocío medio diario en grados Celsius",
                    "Velocidad media diaria del viento en km/h",
                    "Presión media diaria en hPa"
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
    st.write(f"Gráfico interactivo de {column}")
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
        name=col_1+str(year)
    ))

    fig.add_trace(go.Scatter(
    x=yearly_data['aligned_date'],
    y=yearly_data[col_2].cumsum(),
    mode='lines',
    name=col_2+str(year)
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
                        .rename(columns = {'high_temp_deg': 'Temperatura máxima mensual (°C)',
                                           'wind_gust_kmh': 'Racha de viento máxima mensual (km/h)',
                                           'rain_10min_mm': 'Precipitación máxima 10-minutal (mm)',
                                           'rain_rate_mmh': 'Máxima intensidad de lluvia (mm/h)'})

    min_monthly_data = daily_data.resample('ME').min()[['low_temp_deg']]\
        .rename(columns= {'low_temp_deg': 'Temperatura mínima mensual (°C)'})

    mean_monthly_data = daily_data\
        .resample('ME').mean()[['temp_out_deg', 'high_temp_deg', 'low_temp_deg' ,'mean_rel_humidity_perc', 'dewpoint_deg', 'wind_speed_kmh', 'mean_pressure_hPa']]\
        .rename(columns={'temp_out_deg': 'Temperatura media mensual (°C)',
                         'high_temp_deg': 'Media mensual de temperaturas máximas (°C)',
                         'low_temp_deg': 'Media mensual de temperaturas mínimas (°C)',
                         'mean_rel_humidity_perc': 'Humedad relativa media mensual (%)',
                         'dewpoint_deg': 'Punto de rocío medio mensual (°C)',
                         'wind_speed_kmh': 'Velocidad media mensual del viento (km/h)',
                         'mean_pressure_hPa': 'Presión media mensual (hPa)'})

    monthly_pcp_data = daily_data.resample('ME').sum()[['pcp (mm)']]
    #group all monthly data
    monthly_data = pd.concat([max_monthly_data, min_monthly_data, mean_monthly_data, monthly_pcp_data], axis = 1).rename(columns = {'pcp (mm)': 'Precipitación mensual (mm)'})
    monthly_data = monthly_data.reset_index()  
    return(monthly_data) 