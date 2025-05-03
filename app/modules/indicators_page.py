import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from common import load_daily_data,\
                   plot_interactive_current,\
                   select_column_box,\
                   plot_interactive_data_by_year


def get_warm_nights_totals(daily_data):
    n_df_warm_nights = []
    n_hot_nights = []
    n_hell_nights = []

    year_min = daily_data.index.min().year
    max_year = daily_data.index.max().year
    years = np.arange(year_min, max_year + 1, 1)

    for year in years:
        daily_data_year = daily_data[ daily_data.index.year == year ]
        n_df_warm_nights.append( len(daily_data_year[ daily_data_year['low_temp_deg'] >=20.0 ]) )
        n_hot_nights.append( len(daily_data_year[ daily_data_year['low_temp_deg'] >=25.0 ]) )
        n_hell_nights.append( len(daily_data_year[ daily_data_year['low_temp_deg'] >=30.0 ]) )   

    n_df_warm_nights = pd.DataFrame(n_df_warm_nights, columns = ['n_days_tmin_gt_20_deg'])
    n_hot_nights = pd.DataFrame(n_hot_nights, columns = ['n_days_tmin_gt_25_deg'])
    n_hell_nights = pd.DataFrame(n_hell_nights, columns = ['n_days_tmin_gt_30_deg'])
    years = pd.DataFrame(years, columns = ['year'])

    n_nights_classific = pd.concat([years, n_df_warm_nights, n_hot_nights, n_hell_nights], axis = 1)
    
    n_nights_classific.rename(columns={"n_days_tmin_gt_20_deg": "Número de días con temperatura mínima >= 20 °C",
                                       "n_days_tmin_gt_25_deg": "Número de días con temperatura mínima >= 25 °C",
                                       "n_days_tmin_gt_30_deg": "Número de días con temperatura mínima >= 30 °C"}, inplace=True)
    n_nights_classific.set_index("year", inplace=True)
    n_nights_classific = n_nights_classific[n_nights_classific.index >= 2021]

    return n_nights_classific


def get_warm_nights_cumsum(daily_data, thres):

    year_min = daily_data.index.min().year
    max_year = daily_data.index.max().year
    years = np.arange(year_min, max_year + 1, 1)
        
    if thres == 20.0:
        df_warm_nights_cumsum = pd.DataFrame()
        col_name = "Total de días con temperatura mínima >= 20 °C"

    if thres == 25.0:
        df_warm_nights_cumsum = pd.DataFrame()
        col_name = "Total de días con temperatura mínima >= 25 °C"

    if thres == 30.0:
        df_warm_nights_cumsum = pd.DataFrame()
        col_name = "Total de días con temperatura mínima >= 30 °C"

    for year in years:

        daily_data_year = daily_data[ daily_data.index.year == year ]
        
        df_warm_nights = daily_data_year[daily_data_year['low_temp_deg'] >= thres]
        df_warm_nights = df_warm_nights.copy()
        
        df_warm_nights[col_name] = np.arange(1, df_warm_nights["pcp (mm)"].count()+1, 1)
        df_warm_nights[col_name] = df_warm_nights[col_name] - 1
        df_warm_nights = df_warm_nights[[col_name]]
        
        df_warm_nights.reset_index(inplace=True)
        daily_data_year.reset_index(inplace=True)
        df_warm_nights = df_warm_nights.merge(daily_data_year, how = "right")

        df_warm_nights.set_index("date", inplace=True)
        df_warm_nights = df_warm_nights[[col_name]].bfill()
        df_warm_nights = df_warm_nights[[col_name]].ffill()
        df_warm_nights = df_warm_nights.convert_dtypes("int")

        df_warm_nights_cumsum = pd.concat([df_warm_nights_cumsum, df_warm_nights], axis = 0)

    return df_warm_nights_cumsum


st.markdown('# Indicadores climáticos')
st.write('En esta página encontrarás diferentes indicadores climáticos')

daily_data = load_daily_data()

st.markdown('## Número de días con temperatura mínima alcanzando diferentes umbrales cálidos')
n_nights_classific = get_warm_nights_totals(daily_data)
df_tropical_nights = get_warm_nights_cumsum(daily_data, thres = 20.0)
df_scorching_nights = get_warm_nights_cumsum(daily_data, thres = 25.0)
df_infernal_nights = get_warm_nights_cumsum(daily_data, thres = 30.0)


col = select_column_box(n_nights_classific, key = n_nights_classific.columns[0])

st.markdown('## Número anual de noches cálidas')
st.dataframe(n_nights_classific, use_container_width=True)

st.markdown('## Noches cálidas acumuladas')
fig = plot_interactive_data_by_year(df_tropical_nights,
                              value_col= "Total de días con temperatura mínima >= 20 °C",
                              title = "Número acumulado de días con temperatura mínima >= 20 °C",
                              yaxis_title = "Número acumulado de días con temperatura mínima >= 20 °C")
st.plotly_chart(fig, use_container_width=True)

fig = plot_interactive_data_by_year(df_scorching_nights,
                              value_col= "Total de días con temperatura mínima >= 25 °C",
                              title = "Número acumulado de días con temperatura mínima >= 25 °C",
                              yaxis_title = "Número acumulado de días con temperatura mínima >= 25 °C")
st.plotly_chart(fig, use_container_width=True)

fig = plot_interactive_data_by_year(df_infernal_nights,
                              value_col= "Total de días con temperatura mínima >= 30 °C",
                              title = "Número acumulado de días con temperatura mínima >= 30 °C",
                              yaxis_title = "Número acumulado de días con temperatura mínima >= 30 °C")
st.plotly_chart(fig, use_container_width=True)

