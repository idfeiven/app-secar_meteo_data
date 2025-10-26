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

import warnings
import numpy as np
import pandas as pd
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
    path_manual_pcp_data = Path(__file__).parent.parent / "data" / "daily_manual_rain_gage_data.xlsx"
    return(path, path_manual_pcp_data)


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
    max_daily_data = data_parsed.drop(["wind_direction", "wind_gust_dir"], axis = 1).set_index('date').resample('D').max()[['high_temp_deg', 'wind_gust_kmh', 'rain_10min_mm', 'rain_rate_mmh', 'pressure_hPa', 'rel_humidity_perc']]
    max_daily_data.rename(columns = {"pressure_hPa": "max_pressure_hPa", "rel_humidity_perc": "max_rel_humidity_perc"}, inplace=True)

    min_daily_data = data_parsed.drop(["wind_direction", "wind_gust_dir"], axis = 1).set_index('date').resample('D').min()[['low_temp_deg', 'pressure_hPa', 'rel_humidity_perc']]
    min_daily_data.rename(columns = {"pressure_hPa": "min_pressure_hPa", "rel_humidity_perc": "min_rel_humidity_perc"}, inplace=True)

    mean_daily_data = data_parsed.drop(["wind_direction", "wind_gust_dir"], axis = 1).set_index('date').resample('D').mean()[['temp_out_deg', 'rel_humidity_perc', 'dewpoint_deg', 'wind_speed_kmh', 'pressure_hPa']]
    mean_daily_data.rename(columns = {"pressure_hPa": "mean_pressure_hPa", "rel_humidity_perc": "mean_rel_humidity_perc"}, inplace=True)

    daily_pcp_data_stn = data_parsed.drop(["wind_direction", "wind_gust_dir"], axis = 1).set_index('date').resample('D').sum()[['rain_10min_mm']].rename(columns = {'rain_10min_mm': 'daily_rain_pws_mm'})
    
    #group all daily data
    daily_data = pd.concat([max_daily_data, min_daily_data, daily_pcp_data_stn, mean_daily_data], axis = 1)
    daily_data = daily_data.reset_index()
    daily_data = daily_data.round(1)

    return(daily_data)


def update_daily_data(daily_data):
    manual_pcp_data = pd.read_excel(path_manual_pcp_data)
    manual_pcp_data.drop(['Unnamed: 0'], axis = 1, inplace=True)
    manual_pcp_data.rename(columns={'pcp (mm)': 'daily_rain_gage_mm'}, inplace=True)
    daily_data = manual_pcp_data.merge(daily_data, how = 'left', on = 'date')
    daily_data.to_excel(Path(__file__).parent.parent / "data" / "secar_daily_data.xlsx")
    return(daily_data)



#--------------------------------MAIN PROGRAM----------------------------------------
print('Recopilando datos...')
path, path_manual_pcp_data = get_path_data()

print('Organizando datos...')
data_parsed = parse_meteo_data(path)

print("Guardando datos 10 minutales...")
data_parsed.to_excel(Path(__file__).parent.parent / "data" / "secar_10min_data.xlsx")

print('Obteniendo datos diarios...')
daily_data = get_daily_data(data_parsed)

print('Actualizando datos diarios...')
daily_data = update_daily_data(daily_data)
