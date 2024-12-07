# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 16:09:40 2021

@author: ivand
"""

'''
Este programa lee los datos meteorológicos de la estación
Palma Secar de la Real y representa datos 10-minutales, diarios
y mensuales
'''

#Importamos módulo de álgebra lineal y matrices
import numpy as np
import pandas as pd
import warnings
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

warnings.filterwarnings('ignore')

#--------------------------------------CONFIG---------------------------------------------

#set cols to delete, to rename, to move, to perform extreme analysis
cols_to_drop = ['Wind.2', 'Wind.3', 'Heat', 'Heat.1' ,'THW', 'Cool', 'In ', 'In', 'In .1',
               'In .2', 'In .3', 'Wind.4', 'In Air', 'Wind.5', 'ISS ', 'Arc.',
               'Unnamed: 0', 'Unnamed: 1']
cols_to_rename = {'date':'date', 'Temp':'temp_out_deg', 'Hi':'high_temp_deg', 'Low':'low_temp_deg', 'Out':'rel_humidity_perc', 'Dew':'dewpoint_deg',
               'Wind':'wind_speed_kmh', 'Wind.1':'wind_direction', 'Hi.1':'wind_gust_kmh', 'Hi.2':'wind_gust_dir', 'Unnamed: 15':'pressure_hPa',
               'Unnamed: 16':'rain_10min_mm', 'Rain':'rain_rate_mmh'}
cols_to_move = ['date', 'temp_out_deg', 'high_temp_deg', 'low_temp_deg', 'rel_humidity_perc', 'dewpoint_deg',
               'wind_speed_kmh', 'wind_direction', 'wind_gust_kmh', 'wind_gust_dir', 'pressure_hPa',
               'rain_10min_mm', 'rain_rate_mmh']
cols =         ['temp_out_deg', 'high_temp_deg', 'low_temp_deg', 'rel_humidity_perc', 'dewpoint_deg', 'wind_speed_kmh',
                'wind_gust_kmh', 'pressure_hPa', 'rain_10min_mm', 'rain_rate_mmh']
cols_data_abs = ['high_temp_deg', 'wind_gust_kmh', 'low_temp_deg', 'temp_out_deg',
       'rel_humidity_perc', 'dewpoint_deg', 'wind_speed_kmh', 'pressure_hPa',
       'pcp (mm)', 'date']

#-----------------------------------------------------------------------------
#-----------------PROCESADO DE DATOS 10-MINUTALES-----------------------------
#----------------------------------------------------------------------------

def get_path_data():
    #we read all the files creating a searching criteria and a list of all of them
    path = Path(__file__).parent.parent / "data" / "data_la_real.txt"
    path_daily_data = Path(__file__).parent.parent / "data" / "secar_daily_data.xlsx"
    return(path, path_daily_data)


def parse_meteo_data(path):
    #Accedemos al directorio en el que se encuentran los datos de la estación Secar
    #de la real (la_real):
    path_data = path
    #Veamos cómo son estos datos: abrimos fichero sabiendo que los 
    #datos están separados por un espacio (\t en expresión regular)
    data = pd.read_csv(path_data, delimiter='\t', low_memory = False)
    #Mostramos los datos y su tipo:
    print('Leyendo y procesando datos de Secar de la Real')
    print("Número de datos = ", len(data))  
    #unimos columnnas de fecha y hora
    data['date'] = data['Unnamed: 0'] + ' ' + data['Unnamed: 1']
    #eliminamos columnas indeseadas:
    data = data.drop(cols_to_drop, axis = 1) 
    # data_true_pcp_daily = data_true_pcp_daily.drop('Unnamed: 2', axis = 1)
    #renombramos columnas
    data = data.rename(columns = cols_to_rename)
    #eliminamos filas innecesarias:
    data = data.drop(data.index[0])
    #convertimos valores nulos en nans
    data = data.replace('-', np.nan, regex = True)
    print('Valores no válidos encontrados:\n', data.isnull().sum())
    #convertimos a valor numérico:
    data = data.set_index(['date', 'wind_direction', 'wind_gust_dir']).apply(pd.to_numeric)
    data = data.reset_index()
    #convertimos a formato fechas:
    data['date'] = pd.to_datetime(data['date'], dayfirst=True)
    #ordenamos columnas:
    data_parsed = data[cols_to_move]
    print('Datos meteorológicos procesados')
    print('')
    return(data_parsed)


def get_daily_data(data_parsed):
    #resample 10-min data to daily data:
    max_daily_data = data_parsed.drop(["wind_direction", "wind_gust_dir"], axis = 1).set_index('date').resample('D').max()[['high_temp_deg', 'wind_gust_kmh', 'rain_10min_mm', 'rain_rate_mmh']]
    min_daily_data = data_parsed.drop(["wind_direction", "wind_gust_dir"], axis = 1).set_index('date').resample('D').min()[['low_temp_deg']]
    mean_daily_data = data_parsed.drop(["wind_direction", "wind_gust_dir"], axis = 1).set_index('date').resample('D').mean()[['temp_out_deg', 'rel_humidity_perc', 'dewpoint_deg', 'wind_speed_kmh', 'pressure_hPa']]
    daily_pcp_data_stn = data_parsed.drop(["wind_direction", "wind_gust_dir"], axis = 1).set_index('date').resample('D').sum()[['rain_10min_mm']].rename(columns = {'rain_10min_mm': 'daily_rain_mm'})
    
    #group all daily data
    daily_data = pd.concat([max_daily_data, min_daily_data, daily_pcp_data_stn, mean_daily_data], axis = 1)
    daily_data = daily_data.reset_index()

    return(daily_data)


def update_daily_data(daily_data):
    daily_data_old = pd.read_excel(path_daily_data)
    daily_data_old.drop(['Unnamed: 0'], axis = 1, inplace=True)
    daily_data = daily_data_old.merge(daily_data, how = 'left', on = 'date')
    daily_data = daily_data[daily_data.columns.drop(list(daily_data.filter(regex='x')))]
    daily_data.columns = daily_data_old.columns
    daily_data.to_excel(Path(__file__).parent.parent / "data" / "secar_daily_data.xlsx")
    return(daily_data)


def get_monthly_data(daily_data):
    #resample daily data to monthly data:
    max_monthly_data = daily_data.set_index('date').resample('m').max()\
                        [['high_temp_deg', 'wind_gust_kmh', 'rain_10min_mm', 'rain_rate_mmh']]\
                        .rename(columns = {'high_temp_deg': 'max_high_temp_deg',
                                           'wind_gust_kmh': 'max_wind_gust_kmh',
                                           'rain_10min_mm': 'max_rain_10min_mm',
                                           'rain_rate_mmh': 'max_rain_rate_mmh'})

    min_monthly_data = daily_data.set_index('date').resample('m').min()[['low_temp_deg']]\
        .rename(columns= {'low_temp_deg': 'min_low_temp_deg'})

    mean_monthly_data = daily_data.set_index('date')\
        .resample('m').mean()[['temp_out_deg', 'high_temp_deg', 'low_temp_deg' ,'rel_humidity_perc', 'dewpoint_deg', 'wind_speed_kmh', 'pressure_hPa']]\
        .rename(columns={'temp_out_deg': 'mean_temp_out_deg',
                         'high_temp_deg': 'mean_high_temp_deg',
                         'low_temp_deg': 'mean_low_temp_deg',
                         'rel_humidity_perc': 'mean_rel_humidity_perc',
                         'dewpoint_deg': 'mean_dewpoint_deg',
                         'wind_speed_kmh': 'mean_wind_speed_kmh',
                         'pressure_hPa': 'mean_pressure_hPa'})

    monthly_pcp_data = daily_data.set_index('date').resample('m').sum()[['pcp (mm)']]
    #group all monthly data
    monthly_data = pd.concat([max_monthly_data, min_monthly_data, mean_monthly_data, monthly_pcp_data], axis = 1).rename(columns = {'pcp (mm)': 'pcp_acum_month_mm'})
    monthly_data = monthly_data.reset_index()  
    return(monthly_data) 


def get_monthly_data_means(monthly_data):
    monthly_data_means = monthly_data.groupby(monthly_data['date'].dt.strftime('%m')).mean()\
        .drop(['max_high_temp_deg', 'max_wind_gust_kmh', 'max_rain_10min_mm', 'max_rain_rate_mmh',
                'min_low_temp_deg'], axis = 1).rename(columns = {'pcp_acum_month_mm': 'mean_pcp_acum_month_mm'})
    return(monthly_data_means)


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
                year_max_extr = pd.DataFrame(year_max, columns = ['year_max'])
            df_max_extr_year_month = pd.concat([year_max_extr, monthly_data_max.reset_index()[['month_max',col]]], axis = 1)#.drop('date', axis = 1)
            df_month_max = pd.concat([df_month_max, df_max_extr_year_month], axis = 1)
    
    df_month_min = pd.DataFrame()
    for col in monthly_data_min.columns:
            year_min = []
            for month in monthly_data_min.index:
                year_min.append(monthly_data[ monthly_data[col] == monthly_data_min[ monthly_data_min.index == month ][col].values[0]]['date'].dt.strftime('%Y').values[0])    
                year_min_extr = pd.DataFrame(year_min, columns = ['year_min'])
            df_min_extr_year_month = pd.concat([year_min_extr, monthly_data_min.reset_index()[['month_min',col]]], axis = 1)#.drop('date', axis = 1)
            df_month_min = pd.concat([df_month_min, df_min_extr_year_month], axis = 1)
    
    df_month_max.to_excel(Path(__file__).parent.parent /"data" / "monthly_data_max.xlsx")
    df_month_min.to_excel(Path(__file__).parent.parent /"data" / "monthly_data_min.xlsx")
    return(df_month_max, df_month_min)


def get_extreme_values_10min(data_parsed):
    max_vals = pd.DataFrame(data_parsed.drop(['date', 'temp_out_deg', 'low_temp_deg', 'wind_direction', 'wind_gust_dir'],axis = 1).max(), columns = ['max_value'])
    date_max_vals = []
    for idx in data_parsed.drop(['date', 'temp_out_deg', 'low_temp_deg', 'wind_direction', 'wind_gust_dir'],axis = 1).idxmax().values:
        date_max_vals.append(data_parsed.iloc[idx]['date'])
    date_max_vals = pd.DataFrame(date_max_vals, columns = ['date_max_vals'])
    max_vals = pd.concat([max_vals.reset_index(), date_max_vals], axis = 1).rename(columns = {'index': 'variable'}).set_index('variable')

    min_vals = pd.DataFrame(data_parsed.drop(['date', 'high_temp_deg', 'wind_speed_kmh', 'wind_gust_kmh', 'wind_direction', 'wind_gust_dir', 'rain_10min_mm', 'rain_rate_mmh'],axis = 1).min(), columns = ['min_value'])
    date_min_vals = []
    for idx in data_parsed.drop(['date', 'high_temp_deg', 'wind_speed_kmh', 'wind_gust_kmh', 'wind_direction', 'wind_gust_dir', 'rain_10min_mm', 'rain_rate_mmh'], axis = 1).idxmin().values:
        date_min_vals.append(data_parsed.iloc[idx]['date'])
    date_min_vals = pd.DataFrame(date_min_vals, columns = ['date_min_vals'])
    min_vals = pd.concat([min_vals.reset_index(), date_min_vals], axis = 1).rename(columns = {'index': 'variable'}).set_index('variable')

    extr_vals = pd.concat([min_vals, max_vals], axis = 1)
    return(extr_vals)


def get_monthly_data_ranking(monthly_data):
    monthly_ranking = pd.DataFrame()
    for col in monthly_data.drop('date', axis = 1).columns:
        monthly_ranking = pd.concat([monthly_ranking, monthly_data.sort_values(by = col, ascending=False).reset_index()[['date', col]] ], axis = 1)
    monthly_ranking.to_excel(Path(__file__).parent.parent /"data" / "monthly_ranking.xlsx")
    return(monthly_ranking)


def get_daily_data_ranking(daily_data):
    daily_ranking = pd.DataFrame()
    for col in daily_data.drop('date', axis = 1).columns:
        daily_ranking = pd.concat([daily_ranking, daily_data.sort_values(by = col, ascending=False).reset_index()[['date', col]] ], axis = 1)
    daily_ranking.to_excel(Path(__file__).parent.parent /"data" / "daily_ranking.xlsx")
    return(daily_ranking)


def get_warm_nights_totals(daily_data):
    n_tropical_nights = []
    n_hot_nights = []
    n_hell_nights = []

    year_min = daily_data.date.min().year
    max_year = daily_data.date.max().year
    years = np.arange(year_min, max_year + 1, 1)

    for year in years:
        daily_data_year = daily_data[ daily_data.date.dt.year == year ]
        n_tropical_nights.append( len(daily_data_year[ daily_data_year['low_temp_deg'] >=20.0 ]) )
        n_hot_nights.append( len(daily_data_year[ daily_data_year['low_temp_deg'] >=25.0 ]) )
        n_hell_nights.append( len(daily_data_year[ daily_data_year['low_temp_deg'] >=30.0 ]) )   

    n_tropical_nights = pd.DataFrame(n_tropical_nights, columns = ['n_days_tmin_gt_20_deg'])
    n_hot_nights = pd.DataFrame(n_hot_nights, columns = ['n_days_tmin_gt_25_deg'])
    n_hell_nights = pd.DataFrame(n_hell_nights, columns = ['n_days_tmin_gt_30_deg'])
    years = pd.DataFrame(years, columns = ['year'])

    n_nights_classific = pd.concat([years, n_tropical_nights, n_hot_nights, n_hell_nights], axis = 1)
    n_nights_classific.to_excel(Path(__file__).parent.parent /"data" / "nights_classif.xlsx")
    return(n_nights_classific)


def calculate_mean_rel_err_pcp_measures(daily_data):
    pcp_data = daily_data[daily_data['pcp (mm)'] > 0.0].dropna()
    y_data = pcp_data['pcp (mm)'].to_numpy()
    x_data = pcp_data['daily_rain_mm'].to_numpy()
    rel_err = (y_data - x_data)/x_data*100.0
    rel_err = pd.DataFrame(rel_err, columns = {'Relative error %'})
    rel_err.replace(np.inf, np.nan, inplace=True)
    rel_err.dropna(inplace=True)
    print(f'Analizados {len(rel_err)} eventos de precipitación')
    print(f'Error medio (%) cometido en medidas de precipitación: {rel_err.mean()}')
    print(f'Error mínimo (%) cometido en medidas de precipitación: {rel_err.min()}')
    print(f'Error máximo (%) cometido en medidas de precipitación: {rel_err.max()}')
    return(rel_err)


def save_extreme_values_10min(extr_vals):
    extr_vals.to_excel(Path(__file__).parent.parent /"data" / "secar_extreme_vals.xlsx")


def save_monthly_data(monthly_data):
    monthly_data.to_excel(Path(__file__).parent.parent /"data" / "secar_monthly_data.xlsx")


def save_monthly_data_means(monthly_data_means):
    monthly_data_means.to_excel(Path(__file__).parent.parent /"data" / "secar_monthly_data_means.xlsx")


def save_monthly_data_extremes(df_month_max, df_month_min):
    df_month_max.to_excel(Path(__file__).parent.parent /"data" / "secar_monthly_data_extremes.xlsx")
    df_month_min.to_excel(Path(__file__).parent.parent /"data" / "secar_monthly_data_extremes.xlsx")
 

#--------------------------------MAIN PROGRAM----------------------------------------
print('Recopilando datos...')
path, path_daily_data = get_path_data()

print('Organizando datos...')
data_parsed = parse_meteo_data(path)
print('Obteniendo extremos 10-minutales...')
extr_vals = get_extreme_values_10min(data_parsed)
print('Guardando extremos 10-minutales...')
save_extreme_values_10min(extr_vals)

print("Guardando datos 10 minutales...")
data_parsed.to_excel(Path(__file__).parent.parent / "data" / "secar_10min_data.xlsx")

print('Obteniendo datos diarios...')
daily_data = get_daily_data(data_parsed)

print('Actualizando datos diarios...')
daily_data = update_daily_data(daily_data)
print('Obteniendo ránking diario...')
daily_ranking = get_daily_data_ranking(daily_data)

print('Obteniendo datos mensuales...')
monthly_data = get_monthly_data(daily_data)
print('Guardando datos mensuales...')
save_monthly_data(monthly_data)

print('Obteniendo medias datos mensuales...')
monthly_data_means = get_monthly_data_means(monthly_data)
print('Guardando medias datos mensuales...')
save_monthly_data_means(monthly_data_means)
print('Obteniendo extremos mensuales...')
df_month_max, df_month_min = get_monthly_data_extremes(monthly_data)
print('Guardando extremos mensuales...')
save_monthly_data_extremes(df_month_max, df_month_min)
print('Obteniendo ránking mensual')
monthly_ranking = get_monthly_data_ranking(monthly_data)
print('Obteniendo extremos de todos los meses...')
df_month_max, df_month_min = get_monthly_data_extremes(monthly_data)
print('Calculando número de noches tropicales, tórridas e infernales')
n_nights_classific = get_warm_nights_totals(daily_data)
