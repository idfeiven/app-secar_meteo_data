import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from common import load_daily_data,\
                   plot_interactive_current,\
                   select_column_box


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
    
    n_nights_classific.rename(columns={"n_days_tmin_gt_20_deg": "Number of days with minimum temperature >= 20 °C",
                                       "n_days_tmin_gt_25_deg": "Number of days with minimum temperature >= 25 °C",
                                       "n_days_tmin_gt_30_deg": "Number of days with minimum temperature >= 30 °C"}, inplace=True)
    n_nights_classific.set_index("year", inplace=True)
    n_nights_classific = n_nights_classific[n_nights_classific.index >= 2021]

    return n_nights_classific


def get_warm_nights_cumsum(daily_data, thres):

    year_min = daily_data.index.min().year
    max_year = daily_data.index.max().year
    years = np.arange(year_min, max_year + 1, 1)
        
    if thres == 20.0:
        df_warm_nights_cumsum = pd.DataFrame()
        col_name = "Total number of days with minimum temperature >= 20 °C"

    if thres == 25.0:
        df_warm_nights_cumsum = pd.DataFrame()
        col_name = "Total number of days with minimum temperature >= 25 °C"

    if thres == 30.0:
        df_warm_nights_cumsum = pd.DataFrame()
        col_name = "Total number of days with minimum temperature >= 30 °C"

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


def plot_daily_annual_warm_nights(df_warm_nights, n_nights_classific, night_type):
    df_warm_nights = df_warm_nights.reset_index()
    year_min = 2021
    max_year = df_warm_nights.date.max().year
    years = np.arange(year_min, max_year + 1, 1)
    fig, axs = plt.subplots(ncols = 1, figsize = (8,6))

    plt.suptitle('Estación meteorológica Secar de la Real (Palma, España) \n Datos diarios. Elevación: 75 m \n',
                 fontsize = 16,
                 fontweight = 'bold')

    if night_type == "tropical":
        max_val = n_nights_classific.max()["Number of days with minimum temperature >= 20 °C"]
        col_cumsum = "Total number of days with minimum temperature >= 20 °C"

    if night_type == "scorching":
        max_val = n_nights_classific.max()["Number of days with minimum temperature >= 25 °C"]
        col_cumsum = "Total number of days with minimum temperature >= 25 °C"

    if night_type == "infernal":
        max_val = n_nights_classific.max()["Number of days with minimum temperature >= 30 °C"]
        col_cumsum = "Total number of days with minimum temperature >= 30 °C"

    for year in years:
        df_warm_nights_year = df_warm_nights[df_warm_nights['date'].dt.year == year]
        df_warm_nights_year = df_warm_nights_year.copy()
        df_warm_nights_year['dates'] = df_warm_nights_year['date'].dt.strftime('%m-%d')       
        df_warm_nights_year.plot('dates', col_cumsum, ax = axs, label = year)

    axs.set_title(col_cumsum, fontsize = 12)
    axs.set_ylabel(col_cumsum)
    axs.set_ylim([0, max_val + 5])

    if night_type == "tropical":
        axs.set_yticks(np.arange(0, max_val + 5, 5))
    if night_type == "scorching" or night_type == "infernal":
        axs.set_yticks(np.arange(0, max_val + 1, 1))

    axs.grid()
    # set monthly locator
    axs.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    # set formatter
    axs.xaxis.set_major_formatter(mdates.DateFormatter('%b'))

    axs.margins(x = 0.0)

    plt.tight_layout()
    st.pyplot(fig)


st.markdown('# Indicators')
st.write('In this page you will find different climate indicators')

daily_data = load_daily_data()

st.markdown('## Number of days with minimum temperature reaching different warm thresholds')
n_nights_classific = get_warm_nights_totals(daily_data)
df_tropical_nights = get_warm_nights_cumsum(daily_data, thres = 20.0)
df_scorching_nights = get_warm_nights_cumsum(daily_data, thres = 25.0)
df_infernal_nights = get_warm_nights_cumsum(daily_data, thres = 30.0)


col = select_column_box(n_nights_classific, key = n_nights_classific.columns[0])

st.markdown('## Annual number of warm nights')
plot_interactive_current(n_nights_classific, column = col)

st.markdown('## Accumulated warm nights')
plot_daily_annual_warm_nights(df_tropical_nights, n_nights_classific, night_type = "tropical")
plot_daily_annual_warm_nights(df_scorching_nights, n_nights_classific, night_type = "scorching")
plot_daily_annual_warm_nights(df_infernal_nights, n_nights_classific, night_type = "infernal")
