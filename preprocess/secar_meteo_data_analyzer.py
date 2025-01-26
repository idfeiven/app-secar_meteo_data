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


#--------------------------------MAIN PROGRAM----------------------------------------
print('Recopilando datos...')
path, path_daily_data = get_path_data()

print('Organizando datos...')
data_parsed = parse_meteo_data(path)

print("Guardando datos 10 minutales...")
data_parsed.to_excel(Path(__file__).parent.parent / "data" / "secar_10min_data.xlsx")

print('Obteniendo datos diarios...')
daily_data = get_daily_data(data_parsed)

print('Actualizando datos diarios...')
daily_data = update_daily_data(daily_data)

print('Calculando número de noches tropicales, tórridas e infernales')
n_nights_classific = get_warm_nights_totals(daily_data)
