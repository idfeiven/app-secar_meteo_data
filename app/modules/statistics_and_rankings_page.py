import warnings
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from common import load_10min_data,\
                   load_daily_data,\
                   select_column_box,\
                   get_dict_rename_cols,\
                   get_monthly_data

warnings.filterwarnings("ignore", category=FutureWarning)

#-----------------------------------FUNCTIONS-----------------------------------#

def get_daily_data_ranking(data):
    # data.rename(columns = get_dict_rename_cols(), inplace=True)
    daily_ranking = pd.DataFrame()
    for col in data.columns:
        daily_ranking = pd.concat([daily_ranking,
                                   data.sort_values(by = col, ascending=False).reset_index()[['date', col]]],
                                   axis = 1)
        daily_ranking.rename(columns = {"date": f"date {col}"}, inplace=True)
    return(daily_ranking)


def get_monthly_data_ranking(monthly_data):
    monthly_ranking = pd.DataFrame()
    for col in monthly_data.drop('date', axis = 1).columns:
        monthly_ranking_var = monthly_data.sort_values(by = col, ascending=False).reset_index()[['date', col]]
        monthly_ranking_var["date"] = monthly_ranking_var["date"].dt.strftime("%Y-%m")
        monthly_ranking_var.rename(columns = {"date": f"Month of {col}"}, inplace = True)
        monthly_ranking = pd.concat([monthly_ranking, monthly_ranking_var], axis = 1)

    return(monthly_ranking)


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


#-----------------------------------MAIN PROGRAM-----------------------------------#

st.markdown("# Valores frecuentes y ránkings")
st.write(
    """En esta sección se pueden visualizar los histogramas de las variables seleccionadas y los ránkings diarios de las variables seleccionadas.
    Se pueden seleccionar las variables a visualizar en los histogramas y los ránkings diarios."""
) 

#Seleccionar un período de tiempo y representar período de tiempo
data = load_daily_data()
raw_data = load_10min_data()

#Crear rosa de los vientos con datos 10-minutales
st.markdown("## Rosa de los vientos")
st.write("Rosa de los vientos con datos 10-minutales")

wind_data = get_wind_data(raw_data)
wind_rose_data = get_df_wind_rose(wind_data)
plot_interactive_wind_rose(wind_rose_data)

# Crear tabla de ránking mensual
st.markdown('## Ránking mensual')
st.write("Ránking mensual de las variables seleccionadas")
monthly_data = get_monthly_data(data)
monthly_ranking = get_monthly_data_ranking(monthly_data)
st.dataframe(monthly_ranking)

# Crear tabla de ránking diario
st.markdown('## Ránking diario')
st.write("Ránking diario de las variables seleccionadas")
data.rename(columns = get_dict_rename_cols(), inplace=True)
daily_ranking = get_daily_data_ranking(data)
st.dataframe(daily_ranking)

# Crear el histograma
st.markdown('## Histograma')
st.write("Histogramas de las variables seleccionadas")
# Seleccionar una variable del dataset
column = select_column_box(data, key = data.columns[0])

st.write(f"Histograma interactivo de {column}. {len(data[column].dropna())} valores usados.")
plot_interactive_histogram(data, column)

