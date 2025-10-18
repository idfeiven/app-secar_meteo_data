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
import matplotlib.pyplot as plt

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

    daily_pcp_data_stn = data_parsed.drop(["wind_direction", "wind_gust_dir"], axis = 1).set_index('date').resample('D').sum()[['rain_10min_mm']].rename(columns = {'rain_10min_mm': 'daily_rain_mm'})
    
    #group all daily data
    daily_data = pd.concat([max_daily_data, min_daily_data, daily_pcp_data_stn, mean_daily_data], axis = 1)
    daily_data = daily_data.reset_index()
    daily_data = daily_data.round(1)

    return(daily_data)


def update_daily_data(daily_data):
    manual_pcp_data = pd.read_excel(path_manual_pcp_data)
    manual_pcp_data.drop(['Unnamed: 0'], axis = 1, inplace=True)
    daily_data = manual_pcp_data.merge(daily_data, how = 'left', on = 'date')
    daily_data.to_excel(Path(__file__).parent.parent / "data" / "secar_daily_data.xlsx")
    return(daily_data)


def calculate_error_metrics(df, col_true='daily_rain_mm', col_est='pcp (mm)'):
    """
    Compara dos columnas cualesquiera de un DataFrame y calcula MAE, RMSE
    y error medio relativo (MAPE, en %) sobre los eventos con precipitación
    (al menos una de las dos columnas > 0).
    Mantiene compatibilidad por defecto con 'pcp (mm)' vs 'daily_rain_mm'.
    Además genera un scatter plot (estimado en x, verdadero en y) con la línea y=x.
    """

    # Validación de columnas
    if col_true not in df.columns or col_est not in df.columns:
        raise ValueError(f"Columnas no encontradas en el DataFrame: {col_true}, {col_est}")

    # Quitamos filas con nulos en las dos columnas relevantes
    df = df.dropna(subset=[col_true, col_est]).copy()

    # Nos centramos en eventos de precipitación (al menos una de las medidas > 0)
    df = df[(df[col_true] > 0) | (df[col_est] > 0)]

    if df.empty:
        print('No hay datos de precipitación para comparar')
        return None

    y = df[col_true].to_numpy(dtype=float)
    x = df[col_est].to_numpy(dtype=float)
    err = y - x

    mae = np.mean(np.abs(err))
    rmse = np.sqrt(np.mean(err**2))

    # MAPE: calcular solo donde la referencia (y) > 0 para evitar división por cero
    mask = y > 0
    if mask.any():
        mape = np.mean(np.abs((y[mask] - x[mask]) / y[mask])) * 100.0
        mape_n = int(mask.sum())
    else:
        mape = np.nan
        mape_n = 0

    print(f'Columnas comparadas: {col_true} (referencia), {col_est} (estimada)')
    print(f'Analizados {len(df)} eventos de precipitación')
    print(f'MAE: {mae:.2f}')
    print(f'RMSE: {rmse:.2f}')
    if mape_n > 0:
        print(f'Error medio relativo (MAPE): {mape:.2f} % (calculado en {mape_n} eventos con referencia > 0)')
    else:
        print('MAPE no disponible: no hay eventos con referencia > 0')

    # --- Scatter plot: estimado (x) vs verdadero (y) con línea y = x ---
    plt.figure(figsize=(6, 6))
    plt.scatter(x, y, alpha=0.7, s=40, edgecolors='w', linewidth=0.5)
    # Límites y línea y=x
    finite_x = x[np.isfinite(x)]
    finite_y = y[np.isfinite(y)]
    if finite_x.size > 0 and finite_y.size > 0:
        lo = min(finite_x.min(), finite_y.min())
        hi = max(finite_x.max(), finite_y.max())
        if lo == hi:
            lo -= 1.0
            hi += 1.0
        pad = (hi - lo) * 0.05
        line_x = [lo - pad, hi + pad]
        plt.plot(line_x, line_x, 'r--', label='y = x')
        plt.xlim(lo - pad, hi + pad)
        plt.ylim(lo - pad, hi + pad)
    plt.xlabel(f'Estimado: {col_est}')
    plt.ylabel(f'Verdadero: {col_true}')
    mape_str = f"{mape:.2f}%" if not np.isnan(mape) else "N/A"
    plt.title(f'{col_true} vs {col_est}\nMAE={mae:.2f}, RMSE={rmse:.2f}, MAPE={mape_str}')
    plt.grid(True, linestyle=':', linewidth=0.5)
    plt.legend()
    plt.gca().set_aspect('equal', adjustable='box')
    plt.tight_layout()
    plt.show()

    return {
        'col_true': col_true,
        'col_est': col_est,
        'mae': float(mae),
        'rmse': float(rmse),
        'mape_perc': (float(mape) if not np.isnan(mape) else None),
        'mape_n': mape_n,
        'n': int(len(df))
    }

def plot_mape_by_precip_intervals(daily_df, col_true='daily_rain_mm', col_est='pcp (mm)'):
    """
    Calcula y representa el MAPE (%) por intervalos de precipitación tomando
    como referencia la columna `col_true` (por defecto 'daily_rain_mm').
    Intervalos: [0,5), [5,10), [10,20), >=20 (mm).
    Devuelve un DataFrame con MAPE y número de eventos por intervalo.
    """
    if col_true not in daily_df.columns:
        raise ValueError(f"Columna verdadera no encontrada: {col_true}")
    if col_est not in daily_df.columns:
        raise ValueError(f"Columna estimada no encontrada: {col_est}")

    df = daily_df.copy()
    # eliminar filas sin datos esenciales
    df = df.dropna(subset=[col_true, col_est]).copy()
    # considerar solo eventos con referencia > 0 (necesario para MAPE)
    df = df[df[col_true] > 0]

    bins = [0, 5, 10, 20, np.inf]
    labels = ['[0,5)', '[5,10)', '[10,20)', '>=20']
    df['pcp_bin'] = pd.cut(df[col_true], bins=bins, right=False, labels=labels)

    def compute_mape(t, e):
        mask = t > 0
        if mask.sum() == 0:
            return np.nan, 0
        mape = np.mean(np.abs((t[mask] - e[mask]) / t[mask])) * 100.0
        return mape, int(mask.sum())

    results = []
    for lab in labels:
        g = df[df['pcp_bin'] == lab]
        if g.empty:
            results.append({'interval': lab, 'mape_perc': np.nan, 'n': 0})
        else:
            mape, n = compute_mape(g[col_true].to_numpy(dtype=float),
                                   g[col_est].to_numpy(dtype=float))
            results.append({'interval': lab, 'mape_perc': (float(mape) if not np.isnan(mape) else np.nan), 'n': n})

    res_df = pd.DataFrame(results).set_index('interval')

    # Plot de barras
    plt.figure(figsize=(10, 6))
    bars = plt.bar(res_df.index, res_df['mape_perc'].fillna(0), color='C0', edgecolor='k', alpha=0.85)
    plt.ylabel('MAPE (%)')
    plt.xlabel('Intervalos de precipitación (mm)')
    plt.title(f'MAPE por intervalo ({col_true} como referencia)')
    plt.grid(axis='y', linestyle=':', linewidth=0.5)

    # Anotar conteos y valor numérico del MAPE
    for bar, (_, row) in zip(bars, res_df.iterrows()):
        h = bar.get_height()
        mape_val = row['mape_perc']
        n_val = int(row['n'])

        # Texto para MAPE: mostrar "N/A" si no hay valor
        if np.isnan(mape_val):
            mape_text = "MAPE: N/A"
        else:
            mape_text = f"MAPE: {mape_val:.1f}%"

        # Para intervalos sin eventos, atenuar barra y anotar en la base
        if n_val == 0:
            bar.set_alpha(0.3)
            plt.text(bar.get_x() + bar.get_width()/2, 0.5, 'n=0', ha='center', va='bottom', fontsize=9, color='red')
            plt.text(bar.get_x() + bar.get_width()/2, 1.2, 'MAPE: N/A', ha='center', va='bottom', fontsize=9, color='red')
        else:
            # colocar MAPE y n por encima de la barra
            offset_mape = max(0.5, 0.02 * h)
            offset_n = offset_mape + 0.9
            plt.text(bar.get_x() + bar.get_width()/2, h + offset_mape, mape_text, ha='center', va='bottom', fontsize=9)
            plt.text(bar.get_x() + bar.get_width()/2, h + offset_n, f"n={n_val}", ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.show()

    return res_df

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

print('Analizando datos de precipitación diarios')
calculate_error_metrics(daily_data)

print('Representando MAPE por intervalos de precipitación')
plot_mape_by_precip_intervals(daily_data)