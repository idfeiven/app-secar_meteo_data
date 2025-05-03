import pandas as pd
import streamlit as st
from common import load_daily_data,\
                   get_dict_rename_cols,\
                   get_monthly_data


def get_extreme_data(data):
    max_vals = pd.DataFrame(data.max().round(1), columns = ['max_value'])
    date_max_vals = pd.DataFrame(data.idxmax().dt.date, columns = ['date_max_value'])
    max_vals = pd.concat([max_vals, date_max_vals], axis = 1)#.rename(columns = {'index': 'variable'}).set_index('variable')

    min_vals = pd.DataFrame(data.min().round(1), columns = ['min_value'])
    date_min_vals = pd.DataFrame(data.idxmin().dt.date, columns = ['date_min_value'])
    min_vals = pd.concat([min_vals, date_min_vals], axis = 1)#.rename(columns = {'index': 'variable'}).set_index('variable')

    extr_vals = pd.concat([min_vals, max_vals], axis = 1)
    extr_vals.rename(get_dict_rename_cols(), inplace=True)
    
    extr_vals.rename(columns = {"min_value": "Mínimo Récord",
                      "date_min_value": "Fecha Mínimo Récord",
                      "max_value": "Máximo Récord",
                      "date_max_value": "Fecha Máximo Récord"}, inplace=True)
    return(extr_vals)


def get_monthly_data_extremes(monthly_data):
    monthly_data_max = monthly_data.groupby(monthly_data['date'].dt.strftime('%m')).max()\
        .drop(['date'], axis = 1)
    monthly_data_max.index.names = ['month_max']

    monthly_data_min = monthly_data.groupby(monthly_data['date'].dt.strftime('%m')).min()\
        .drop(['date'], axis = 1)
    monthly_data_min.index.names = ['month_min']

    df_month_max = pd.DataFrame()
    for col in monthly_data_max.columns:
            year_max = []
            for month in monthly_data_max.index:
                year_max.append(monthly_data[ monthly_data[col] == monthly_data_max[ monthly_data_max.index == month ][col].values[0]]['date'].dt.strftime('%Y').values[0])    
                year_max_extr = pd.DataFrame(year_max, columns = [f'Year of max {col}'])
            df_max_extr_year_month = pd.concat([year_max_extr, monthly_data_max.reset_index()[['month_max',col]]], axis = 1)#.drop('date', axis = 1)
            df_month_max = pd.concat([df_month_max, df_max_extr_year_month], axis = 1)
    df_month_max.columns = df_month_max.columns.str.replace("Monthly", "Monthly max")
    
    df_month_min = pd.DataFrame()
    for col in monthly_data_min.columns:
            year_min = []
            for month in monthly_data_min.index:
                year_min.append(monthly_data[ monthly_data[col] == monthly_data_min[ monthly_data_min.index == month ][col].values[0]]['date'].dt.strftime('%Y').values[0])    
                year_min_extr = pd.DataFrame(year_min, columns = [f'Year of min {col}'])
            df_min_extr_year_month = pd.concat([year_min_extr, monthly_data_min.reset_index()[['month_min',col]]], axis = 1)#.drop('date', axis = 1)
            df_month_min = pd.concat([df_month_min, df_min_extr_year_month], axis = 1)
    df_month_min.columns = df_month_min.columns.str.replace("Monthly", "Monthly min")


    df_month_max = df_month_max.loc[:,~df_month_max.columns.str.contains("month_")].copy()
    df_month_max["Month"] = [1,2,3,4,5,6,7,8,9,10,11,12]
    df_month_max.set_index("Month", inplace=True)

    df_month_min = df_month_min.loc[:,~df_month_min.columns.str.contains("month_")].copy()
    df_month_min["Month"] = [1,2,3,4,5,6,7,8,9,10,11,12]
    df_month_min.set_index("Month", inplace=True)

    return df_month_max, df_month_min


st.markdown("# Datos extremos")
st.write(
    """En esta página puedes inspeccionar los datos extremos de la
    estación meteorológica"""
)

# Cargar el dataset desde un archivo local
data = load_daily_data()
monthly_data = get_monthly_data(data)

#Calculate extreme weather data
st.markdown("## Extremos diarios")
extr_data = get_extreme_data(data)
st.dataframe(extr_data)

# Calculate monthly extremes
df_month_max, df_month_min = get_monthly_data_extremes(monthly_data)

st.markdown("## Monthly extremes")

st.markdown("### Monthly maximum records")
st.dataframe(df_month_max)

st.markdown("### Monthly minimum records")
st.dataframe(df_month_min)
