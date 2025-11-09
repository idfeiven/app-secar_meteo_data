import calendar
import pandas as pd
import streamlit as st
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from common import load_daily_data,\
                   get_dict_rename_cols,\
                   get_monthly_data,\
                   select_column_box

# ----------------------------------FUNCTIONS-----------------------------------#

def plot_percentiles_calendar(daily_data, column, year, cmap = 'RdBu_r'):

    df_percentiles = _get_daily_percentiles(daily_data, column)
    df_pivot = _get_percentiles_calendar(df_percentiles, year)

    # Crear el mapa de calor
    plt.figure(figsize=(20, 8))
    ax = sns.heatmap(df_pivot, annot=True, fmt=".0f", cmap=cmap, center=50, 
                linewidths=0.5, linecolor='gray', cbar_kws={'label': 'Percentil'},
                annot_kws={"size": 10, "weight": "bold"},)

    # Activar ticks en los 4 lados
    ax.tick_params(
        axis='both',       # aplicar a ambos ejes
        which='both',      # mayor y menor (aunque no usamos menores aquí)
        top=True,          # ticks arriba
        bottom=True,       # ticks abajo
        left=True,         # ticks izquierda
        right=True         # ticks derecha
    )

    # Mostrar etiquetas también en la parte superior y derecha
    ax.xaxis.set_tick_params(labeltop=True)
    ax.yaxis.set_tick_params(labelright=True)

    # Ajustes de estilo
    plt.suptitle(f'Calendario de Percentiles de {column}. Año {year}', fontsize=16, fontweight ='bold')
    plt.title('Palma Secar de la Real', fontsize=10, loc='left')
    plt.title('Gráfico: Iván Domínguez Fuentes', fontsize=10, loc='center')
    plt.title('Datos desde 06/02/2021. Precipitación desde 2014.', fontsize=10, loc='right')
    plt.xlabel('Día del mes', fontweight ='bold')
    plt.ylabel('Mes', fontweight ='bold')
    plt.xticks(rotation=0)
    plt.yticks(rotation=0)
    plt.tight_layout()
    st.pyplot(plt.gcf())  # Mostrar el gráfico en Streamlit


def _get_daily_percentiles(daily_data, column):

    #Seleccionamos variable para el cálculo de percentiles
    df = daily_data[[column]].copy()

    #Si los datos seleccionados son de precipitación, nos quedamos sólo con los valores no nulos
    if df.columns.str.contains('mm'):
        df = df[df[column] > 0]

    # Definimos los percentiles a calcular
    percentiles = np.arange(0, 101, 1)  # De 0 a 100 en pasos de 1
    # Calculamos los percentiles para cada mes del año

    for month in range(1, 13):  # De enero (1) a diciembre (12)
        month_data = df[df.index.month == month]  # Filtramos los datos del mes actual
        month_percentiles = month_data[column].quantile(percentiles / 100)  # Calculamos los percentiles
        #Interpolamos los valores para asignar un valor entre 0 y 100 para el percentil
        df.loc[df.index.month == month, 'Percentil'] = np.interp(month_data[column], month_percentiles, month_percentiles.index)  
        # Redondeamos los percentiles a 2 decimales
        df['Percentil'] = df['Percentil'].round(2)
    
    return df


def _get_percentiles_calendar(df_percentiles, year):
    # Crear un DataFrame vacío para almacenar los datos
    data = []

    for month in range(1, 13):  # De enero (1) a diciembre (12)
        days_in_month = calendar.monthrange(year, month)[1]
        for day in range(1, days_in_month + 1):
            percentile_val = df_percentiles[(df_percentiles.index.year == year) & (df_percentiles.index.month == month) & (df_percentiles.index.day == day)]['Percentil'].values
            if len(percentile_val) > 0:
                percentile_val = percentile_val[0]
                data.append({
                    'Mes': calendar.month_abbr[month],
                    'Día': day,
                    'Percentil': percentile_val * 100 # Percentiles entre 0 y 100
                })
            else:
                data.append({
                    'Mes': calendar.month_abbr[month],
                    'Día': day,
                    'Percentil': np.nan  # Si no hay datos, asignar NaN
                })
    # Crear DataFrame
    df = pd.DataFrame(data)


    # Pivotar para que los meses sean las filas y los días las columnas
    df_pivot = df.pivot(index='Mes', columns='Día', values='Percentil')

    # Asegurar el orden correcto de los meses
    meses_orden = [calendar.month_abbr[m] for m in range(1, 13)]
    df_pivot = df_pivot.reindex(meses_orden)

    return df_pivot


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

# ----------------------------------MAIN PROGRAM-----------------------------------#
st.set_page_config(page_title="Valores extremos", page_icon="🌡️", layout="wide")

st.markdown("# Datos extremos")
st.write(
    """En esta página puedes inspeccionar los datos extremos de la
    estación meteorológica"""
)

# Cargar el dataset desde un archivo local
data = load_daily_data()
data = data.drop(columns=['correction', 'storm', 'daily_rain_pws_mm', 'daily_rain_gage_mm'])
monthly_data = get_monthly_data(data)
data.rename(columns = get_dict_rename_cols(), inplace=True)

# Crar el calendario de percentiles
st.markdown('## ¿Es hoy un día extremo?')
st.write("Calendario de percentiles de las variables seleccionadas")
st.write("Idea original extraída de hoyextremo.com")
column = select_column_box(data, key = data.columns[0])
year = st.selectbox("Selecciona el año", data.index.year.unique(), index = data.index.year.unique().shape[0] -1)
if 'mm' in column:
    cmap = 'viridis_r'
elif 'km/h' in column:
    cmap = 'BuPu_r'
elif 'hPa' in column:
    cmap = 'YlGnBu_r'
elif '%' in column:
    cmap = 'RdBu_r'
else:
    cmap = 'RdBu_r'
st.write(f"Calendario de percentiles de {column}. Año {year}.")
plot_percentiles_calendar(data, column, year, cmap = cmap)

#Calculate extreme weather data
st.markdown("## Extremos diarios")
extr_data = get_extreme_data(data)
st.dataframe(extr_data)

# Calculate monthly extremes
df_month_max, df_month_min = get_monthly_data_extremes(monthly_data)

st.markdown("## Extremos mensuales")

st.markdown("### Records máximos mensuales")
st.dataframe(df_month_max)

st.markdown("### Records mínimos mensuales")
st.dataframe(df_month_min)
