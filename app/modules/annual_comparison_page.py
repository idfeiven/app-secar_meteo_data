import streamlit as st
from recent_data_page import _load_daily_data
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
import pandas as pd


def _plot_daily_annual_comp_temp(daily_data):
    daily_data = daily_data.reset_index()
    year_min = 2021
    max_year = daily_data.date.max().year
    years = np.arange(year_min, max_year + 1, 1)
    fig, axs = plt.subplots(nrows = 3, ncols = 1, figsize = (12,16))
    plt.suptitle('Estación meteorológica Secar de la Real (Palma, España) \n Datos diarios. Elevación: 75 m \n', fontsize = 16, fontweight = 'bold')

    # dates = daily_data[daily_data['date'].dt.year == 2022]['date'].dt.strftime('%m-%d')

    for year in years:
        daily_data_year = daily_data[daily_data['date'].dt.year == year]
        daily_data_year.loc[:, 'date'] = daily_data_year['date'].dt.strftime('%m-%d')
        # daily_data_year.set_index('date', inplace = True)
        
        daily_data_year.plot('date', 'high_temp_deg', ax = axs[0], label = year)
        daily_data_year.plot('date', 'low_temp_deg', ax = axs[1], label = year)
        daily_data_year.plot('date', 'temp_out_deg', ax = axs[2], label = year)    

    axs[0].set_title('Temperatura máxima diaria', fontsize = 12)
    axs[0].set_title(f'Validez datos de temperatura: 2021-{str(max_year)}', fontsize = 9, loc = 'right')        
    axs[0].set_ylabel('T (°C)')
    # axs[0].set_xlim([dates.min(), dates.max()])

    axs[1].set_title('Temperatura mínima diaria', fontsize = 12)
    axs[1].set_ylabel('T (°C)')
    # axs[1].set_xlim([dates.min(), dates.max()])

    axs[2].set_title('Temperatura media diaria', fontsize = 12)
    axs[2].set_ylabel('T (°C)')
    # axs[2].set_xlim([dates.min(), dates.max()])

    for ax in axs:
        ax.grid()
        # set monthly locator
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        # set formatter
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))

        ax.margins(x = 0.0)

    plt.tight_layout()
    st.pyplot(fig)


def _get_monthly_data(daily_data):
    #resample daily data to monthly data:
    max_monthly_data = daily_data.resample('m').max()\
                        [['high_temp_deg', 'wind_gust_kmh', 'rain_10min_mm', 'rain_rate_mmh']]\
                        .rename(columns = {'high_temp_deg': 'max_high_temp_deg',
                                           'wind_gust_kmh': 'max_wind_gust_kmh',
                                           'rain_10min_mm': 'max_rain_10min_mm',
                                           'rain_rate_mmh': 'max_rain_rate_mmh'})

    min_monthly_data = daily_data.resample('m').min()[['low_temp_deg']]\
        .rename(columns= {'low_temp_deg': 'min_low_temp_deg'})

    mean_monthly_data = daily_data\
        .resample('m').mean()[['temp_out_deg', 'high_temp_deg', 'low_temp_deg' ,'rel_humidity_perc', 'dewpoint_deg', 'wind_speed_kmh', 'pressure_hPa']]\
        .rename(columns={'temp_out_deg': 'mean_temp_out_deg',
                         'high_temp_deg': 'mean_high_temp_deg',
                         'low_temp_deg': 'mean_low_temp_deg',
                         'rel_humidity_perc': 'mean_rel_humidity_perc',
                         'dewpoint_deg': 'mean_dewpoint_deg',
                         'wind_speed_kmh': 'mean_wind_speed_kmh',
                         'pressure_hPa': 'mean_pressure_hPa'})

    monthly_pcp_data = daily_data.resample('m').sum()[['pcp (mm)']]
    #group all monthly data
    monthly_data = pd.concat([max_monthly_data, min_monthly_data, mean_monthly_data, monthly_pcp_data], axis = 1).rename(columns = {'pcp (mm)': 'pcp_acum_month_mm'})
    monthly_data = monthly_data.reset_index()  
    return(monthly_data) 


def _get_monthly_data_means(monthly_data):
    monthly_data_means = monthly_data.groupby(monthly_data['date'].dt.strftime('%m')).mean()\
        .drop(['max_high_temp_deg', 'max_wind_gust_kmh', 'max_rain_10min_mm', 'max_rain_rate_mmh',
                'min_low_temp_deg'], axis = 1).rename(columns = {'pcp_acum_month_mm': 'mean_pcp_acum_month_mm'})
    return(monthly_data_means)


def _plot_daily_annual_comp_pcp(daily_data):
    daily_data = daily_data.reset_index()
    year_min = daily_data.date.min().year
    max_year = daily_data.date.max().year
    years = np.arange(year_min, max_year + 1, 1)
    fig, axs = plt.subplots(nrows = 2, ncols = 1, figsize = (16,12))
    plt.suptitle('Estación meteorológica Secar de la Real (Palma, España) \n Datos diarios. Elevación: 75 m \n', fontsize = 16, fontweight = 'bold')

    for year in years:
        daily_data_year = daily_data[daily_data['date'].dt.year == year]
        daily_data_year = daily_data_year.copy()
        daily_data_year.loc[:, 'pcp_acum_mm'] = daily_data_year['pcp (mm)'].cumsum()
        daily_data_year.loc[:, 'date'] = daily_data_year['date'].dt.strftime('%m-%d')
        # daily_data_year.set_index('date', inplace = True)
        
        daily_data_year.plot('date', 'pcp (mm)', ax = axs[0], legend = True, label = year)    
        daily_data_year.plot('date', 'pcp_acum_mm', ax = axs[1], legend = True, label = year)    

    #plot accumulated pcp daily mean sum
    pcp_mean_daily_cumsum = daily_data['pcp (mm)'].groupby(daily_data['date'].dt.strftime('%m-%d')).mean().cumsum()
    axs[1].plot(pcp_mean_daily_cumsum.index, pcp_mean_daily_cumsum, c = 'black', lw = 3, label = 'Media')

    axs[0].set_title('Precipitación diaria', fontsize = 12)
    axs[0].set_title(f'Validez datos de precipitación: 2014-{str(max_year)}', fontsize = 9, loc = 'right')            
    axs[0].set_ylabel('Prec. (mm)')

    axs[1].set_title('Precipitación acumulada', fontsize = 12)
    axs[1].set_title(f'Validez datos de precipitación: 2014-{str(max_year)}', fontsize = 9, loc = 'right')            
    axs[1].set_ylabel('Prec. (mm)')
    axs[1].legend()

    plt.gca().set_ylim(bottom=0)

    for ax in axs:
        ax.grid()
        # set monthly locator
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        # # set formatter
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    
        ax.margins(x = 0.0)

    plt.tight_layout()
    st.pyplot(fig)


def _plot_sensor_comparison_daily_data_pcp_current_year(daily_data):
    daily_data.reset_index(inplace = True)
    max_year = daily_data.date.max().year
    fig, axs = plt.subplots(nrows = 1, ncols = 1, figsize = (12,8))
    plt.suptitle('Estación meteorológica Secar de la Real (Palma, España) \n Datos diarios. Elevación: 75 m \n', fontsize = 16, fontweight = 'bold')

    daily_data_year = daily_data[daily_data['date'].dt.year == max_year]
    daily_data_year = daily_data_year.copy()
    daily_data_year.loc[:, 'pcp_acum_man_mm'] = daily_data_year['pcp (mm)'].cumsum()
    daily_data_year.loc[:, 'pcp_acum_pws_mm'] = daily_data_year['daily_rain_mm'].cumsum()

    daily_data_year.loc[:, 'date'] = daily_data_year['date'].dt.strftime('%m-%d')
    # daily_data_year.set_index('date', inplace = True)
    
    axs.set_title(f"Pluvio manual: {np.round(daily_data_year.pcp_acum_man_mm.max(), 1)} mm", loc = 'left', fontsize = 10, fontweight = 'bold')
    axs.set_title(f"Pluvio Vantage Vue: {np.round(daily_data_year.pcp_acum_pws_mm.max(), 1)} mm", loc = 'right', fontsize = 10, fontweight = 'bold')

    daily_data_year.plot('date', 'pcp_acum_man_mm', ax= axs, legend = True, color = 'blue', label = f"Pluviómetro manual {max_year}")    
    daily_data_year.plot('date', 'pcp_acum_pws_mm', ax= axs, legend = True, color = 'darkturquoise', label = f"Pluviómetro Davis Vantage Vue {max_year}")    
    #plot accumulated pcp daily mean sum
    pcp_mean_daily_cumsum = daily_data['pcp (mm)'].groupby(daily_data['date'].dt.strftime('%m-%d')).mean().cumsum()
    axs.plot(pcp_mean_daily_cumsum.index, pcp_mean_daily_cumsum, c = 'black', lw = 3, label = f'Media 2014-{max_year}')

    axs.set_title('Precipitación diaria acumulada', fontsize = 12)
    axs.set_title(f'Validez datos de precipitación pluvio manual: 2014-{str(max_year)} \n Validez datos de precipitación Vantage Vue: 2021-{str(max_year)}', fontsize = 9)            
    axs.set_ylabel('Prec. (mm)')

    plt.gca().set_ylim(bottom=0)

    axs.grid()
    axs.legend()
    # set monthly locator
    axs.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    # # set formatter
    axs.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    
    axs.margins(x = 0.0)

    plt.tight_layout()
    st.pyplot(fig)


def _plot_monthly_data_temp(monthly_data, monthly_data_means):
    year_min = 2021
    max_year = monthly_data.date.max().year
    years = np.arange(year_min, max_year + 1, 1)
    fig, axs = plt.subplots(nrows = 3, ncols = 1, figsize = (12,16))
    fig.suptitle('Estación meteorológica Secar de la Real (Palma, España) \n Datos mensuales. Elevación: 75 m \n', fontsize = 16, fontweight = 'bold')
    for year in years:
        monthly_data_year = monthly_data[monthly_data['date'].dt.year == year]
        monthly_data_year = monthly_data_year.copy()
        monthly_data_year.loc[:, 'date'] = monthly_data_year['date'].dt.strftime('%m')
        # daily_data_year.set_index('date', inplace = True)
        axs[0].plot(monthly_data_year['date'], monthly_data_year['mean_high_temp_deg'], label = year)
        axs[1].plot(monthly_data_year['date'], monthly_data_year['mean_low_temp_deg'], label = year)
        axs[2].plot(monthly_data_year['date'], monthly_data_year['mean_temp_out_deg'], label = year)
    axs[0].plot(monthly_data_means.index, monthly_data_means['mean_high_temp_deg'], c = 'black', lw = 3, label = f'Media')
    axs[1].plot(monthly_data_means.index, monthly_data_means['mean_low_temp_deg'], c = 'black', lw = 3, label = f'Media')
    axs[2].plot(monthly_data_means.index, monthly_data_means['mean_temp_out_deg'], c = 'black', lw = 3, label = f'Media')
    
    # dateticks_format = DateFormatter('%b')

    axs[0].set_title('Temperatura máxima media mensual', fontsize = 12)
    axs[0].set_title(f'Validez datos de temperatura: 2021-{str(max_year)}', fontsize = 9, loc = 'right')    
    axs[0].set_ylabel('T (°C)')
    axs[0].set_xlabel('Mes del año')
    axs[0].set_xlim([monthly_data_means.index.min(), monthly_data_means.index.max()])
    axs[0].grid()
    axs[0].legend()

    axs[1].set_title('Temperatura mínima media mensual', fontsize = 12)
    axs[1].set_ylabel('T (°C)')
    axs[1].set_xlabel('Mes del año')
    axs[1].set_xlim([monthly_data_means.index.min(), monthly_data_means.index.max()])
    axs[1].grid()
    axs[1].legend()

    axs[2].set_title('Temperatura media mensual', fontsize = 12)
    axs[2].set_ylabel('T (°C)')
    axs[2].set_xlabel('Mes del año')
    axs[2].set_xlim([monthly_data_means.index.min(), monthly_data_means.index.max()])
    axs[2].grid()
    axs[2].legend()
    
    plt.tight_layout()
    st.pyplot(fig)


def _plot_monthly_yearly_data_pcp(monthly_data, monthly_data_means):
    year_min = monthly_data.date.min().year
    max_year = monthly_data.date.max().year
    years = np.arange(year_min, max_year + 1, 1)
    fig, axs = plt.subplots(nrows = 2, ncols = 1, figsize = (16,12))
    fig.suptitle('Estación meteorológica Secar de la Real (Palma, España) \n Datos mensuales. Elevación: 75 m \n', fontsize = 16, fontweight = 'bold')
    for year in years:
        monthly_data_year = monthly_data[monthly_data['date'].dt.year == year]
        monthly_data_year['date'] = monthly_data_year['date'].dt.strftime('%m')
        # daily_data_year.set_index('date', inplace = True)
        axs[0].plot(monthly_data_year['date'], monthly_data_year['pcp_acum_month_mm'], label = year)
    axs[0].plot(monthly_data_means.index, monthly_data_means['mean_pcp_acum_month_mm'], c = 'black', lw = 3, label = f'Media')
    bar = axs[1].bar(years, monthly_data.set_index('date').resample('Y').sum()['pcp_acum_month_mm'], color = 'blue')
    axs[1].bar_label(bar)
    # dateticks_format = DateFormatter('%b')

    axs[0].set_title('Precipitación mensual', fontsize = 12)
    axs[0].set_title(f'Validez datos de precipitación: 2014-{str(max_year)}', fontsize = 9, loc = 'right')        
    axs[0].set_ylabel('Prec. (mm)')
    axs[0].set_xlabel('Mes del año')
    axs[0].set_xlim([monthly_data_means.index.min(), monthly_data_means.index.max()])
    axs[0].grid()
    axs[0].legend()

    axs[1].set_title('Precipitación anual', fontsize = 12)
    axs[1].set_title(f'Validez datos de precipitación: 2014-{str(max_year)}', fontsize = 9, loc = 'right')        
    axs[1].set_ylabel('Prec. (mm)')
    axs[1].set_xlabel('Año')
    axs[1].set_xticks(years)
    axs[1].grid()
    
    plt.tight_layout()
    st.pyplot(fig)


def annual_comparison_page():

    st.markdown("# Annual data comparison")
    st.write("In this page you can find daily data comparisons between different years")

    st.text("Please note that there are 2 precipitation series: one with manual \n \
        records and the other with data from the automatic weather station. \n \
        The plotted data showed here are the precipitation from manual rain gauge.")

    st.markdown("## Daily Temperature")

    daily_data = _load_daily_data()
    _plot_daily_annual_comp_temp(daily_data)
    monthly_data = _get_monthly_data(daily_data)
    monthly_data_means = _get_monthly_data_means(monthly_data)

    st.markdown("## Daily Precipitation")
    _plot_daily_annual_comp_pcp(daily_data)
    _plot_sensor_comparison_daily_data_pcp_current_year(daily_data)

    st.markdown("## Monthly Temperature")
    _plot_monthly_data_temp(monthly_data, monthly_data_means)

    st.markdown("## Monthly and yearly Precipitation")
    _plot_monthly_yearly_data_pcp(monthly_data, monthly_data_means)