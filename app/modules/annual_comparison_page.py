import numpy as np
import pandas as pd
import streamlit as st
from common import load_daily_data,\
                   plot_interactive_data_by_year,\
                   plot_interactive_comparison_cumulative_data


# -----------------------------------FUNCTIONS-----------------------------------

def get_monthly_data_for_plots(daily_data):
    #resample daily data to monthly data:
    max_monthly_data = daily_data.resample('ME').max()\
                        [['high_temp_deg', 'wind_gust_kmh', 'rain_10min_mm', 'rain_rate_mmh']]\
                        .rename(columns = {'high_temp_deg': 'max_high_temp_deg',
                                           'wind_gust_kmh': 'max_wind_gust_kmh',
                                           'rain_10min_mm': 'max_rain_10min_mm',
                                           'rain_rate_mmh': 'max_rain_rate_mmh'})

    min_monthly_data = daily_data.resample('ME').min()[['low_temp_deg']]\
        .rename(columns= {'low_temp_deg': 'min_low_temp_deg'})

    mean_monthly_data = daily_data\
        .resample('ME').mean()[['temp_out_deg', 'high_temp_deg', 'low_temp_deg' ,'mean_rel_humidity_perc', 'dewpoint_deg', 'wind_speed_kmh', 'mean_pressure_hPa']]\
        .rename(columns={'temp_out_deg': 'mean_temp_out_deg',
                         'high_temp_deg': 'mean_high_temp_deg',
                         'low_temp_deg': 'mean_low_temp_deg',
                         'dewpoint_deg': 'mean_dewpoint_deg',
                         'wind_speed_kmh': 'mean_wind_speed_kmh',
                         'mean_pressure_hPa': 'mean_pressure_hPa'})

    monthly_pcp_data = daily_data.resample('ME').sum()[['pcp (mm)']]
    #group all monthly data
    monthly_data = pd.concat([max_monthly_data, min_monthly_data, mean_monthly_data, monthly_pcp_data], axis = 1).rename(columns = {'pcp (mm)': 'pcp_acum_month_mm'})
    monthly_data = monthly_data.reset_index()  
    return(monthly_data) 


def get_monthly_data_means(monthly_data):
    monthly_data_means = monthly_data.groupby(monthly_data['date'].dt.strftime('%m')).mean()\
        .drop(['max_high_temp_deg', 'max_wind_gust_kmh', 'max_rain_10min_mm', 'max_rain_rate_mmh',
                'min_low_temp_deg'], axis = 1).rename(columns = {'pcp_acum_month_mm': 'mean_pcp_acum_month_mm'})
    
    return(monthly_data_means)


# -----------------------------------MAIN PROGRAM-----------------------------------

st.markdown("# Annual data comparison")
st.write("In this page you can find daily data comparisons between different years")

st.text("Please note that there are 2 precipitation series: one with manual \n \
    records and the other with data from the automatic weather station. \n \
    The plotted data showed here are the precipitation from manual rain gauge.")

# get the data
daily_data = load_daily_data()
monthly_data = get_monthly_data_for_plots(daily_data)
monthly_data_means = get_monthly_data_means(monthly_data)
monthly_data.set_index('date', inplace = True)
monthly_data_means.set_index('date', inplace = True)

st.markdown("## Daily Temperature")
fig = plot_interactive_data_by_year(daily_data, 'high_temp_deg', "Temperatura máxima diaria", "T (°C)")
st.plotly_chart(fig, use_container_width=True)

fig = plot_interactive_data_by_year(daily_data, 'low_temp_deg', "Temperatura mínima diaria", "T (°C)")
st.plotly_chart(fig, use_container_width=True)

fig = plot_interactive_data_by_year(daily_data, 'temp_out_deg', "Temperatura media diaria", "T (°C)")
st.plotly_chart(fig, use_container_width=True)

st.markdown("## Daily Humidity")
fig = plot_interactive_data_by_year(daily_data, 'max_rel_humidity_perc', "Humedad máxima diaria", "T (°C)")
st.plotly_chart(fig, use_container_width=True)

fig = plot_interactive_data_by_year(daily_data, 'min_rel_humidity_perc', "Humedad mínima diaria", "T (°C)")
st.plotly_chart(fig, use_container_width=True)

fig = plot_interactive_data_by_year(daily_data, 'mean_rel_humidity_perc', "Humedad media diaria", "T (°C)")
st.plotly_chart(fig, use_container_width=True)

st.markdown("## Daily Precipitation")
fig = plot_interactive_data_by_year(daily_data, 'pcp (mm)', "Precipitación diaria", "mm")
st.plotly_chart(fig, use_container_width=True)

fig = plot_interactive_comparison_cumulative_data(daily_data,
                                                  2025,
                                                  'pcp (mm)',
                                                  'daily_rain_mm',
                                                  'pcp (mm)',
                                                  "Precipitación diaria acumulada",
                                                  "mm")
st.plotly_chart(fig, use_container_width=True)

st.markdown("## Daily wind speed and gusts")
fig = plot_interactive_data_by_year(daily_data, 'wind_speed_kmh', "Velocidad media diaria", "km/h")
st.plotly_chart(fig, use_container_width=True)

fig = plot_interactive_data_by_year(daily_data, 'wind_gust_kmh', "Racha máxima diaria", "km/h")
st.plotly_chart(fig, use_container_width=True)

st.markdown("## Daily Mean Sea Level Pressure")
fig = plot_interactive_data_by_year(daily_data, 'max_pressure_hPa', "Presión barométrica máxima diaria", "hPa")
st.plotly_chart(fig, use_container_width=True)

fig = plot_interactive_data_by_year(daily_data, 'min_pressure_hPa', "Presión barométrica mínima diaria", "hPa")
st.plotly_chart(fig, use_container_width=True)

fig = plot_interactive_data_by_year(daily_data, 'mean_pressure_hPa', "Presión barométrica media diaria", "hPa")
st.plotly_chart(fig, use_container_width=True)

st.markdown("## Monthly Temperature")
fig = plot_interactive_data_by_year(monthly_data, 'mean_high_temp_deg', "Temperatura máxima media mensual", "T (°C)")
st.plotly_chart(fig, use_container_width=True)

fig = plot_interactive_data_by_year(monthly_data, 'mean_low_temp_deg', "Temperatura mínima media mensual", "T (°C)")
st.plotly_chart(fig, use_container_width=True)

fig = plot_interactive_data_by_year(monthly_data, 'mean_temp_out_deg', "Temperatura media mensual", "T (°C)")
st.plotly_chart(fig, use_container_width=True)

st.markdown("## Monthly and yearly Precipitation")
fig = plot_interactive_data_by_year(monthly_data, 'pcp_acum_month_mm', "Precipitación acumulada mensual", "mm")
st.plotly_chart(fig, use_container_width=True)

st.markdown("## Monthly data in table")
monthly_data = monthly_data.copy()
monthly_data['date'] = monthly_data.index
monthly_data = monthly_data.reset_index(drop=True)
monthly_data.sort_values(by = "date", ascending = False, inplace=True)
monthly_data["date"]= monthly_data["date"].dt.strftime("%Y-%m")
monthly_data = monthly_data.round(2)

monthly_data.rename(columns = {'date': "Year and month",
                               'max_high_temp_deg': 'Monthly max. temperature (°C)',
                               'max_wind_gust_kmh': 'Monthly max. wind gust (km/h)',
                               'max_rain_10min_mm': 'Monthly max. rain in 10 minutes (mm)',
                               'max_rain_rate_mmh': 'Monthly max. instantaneous rain rate (mm/h)',
                               'mean_temp_out_deg': 'Monthly mean temperature (°C)',
                               'min_low_temp_deg': "Monthly min. temperature (°C)",
                               'pcp_acum_month_mm': "Monthly Precipitation (mm)",
                               'mean_high_temp_deg': 'Monthly mean max. temperatures (°C)',
                               'mean_low_temp_deg': 'Monthly mean min. temperatures (°C)',
                               'mean_rel_humidity_perc': 'Monthly mean relative humidity (%)',
                               'mean_dewpoint_deg': 'Monthly mean dewpoint (°C)',
                               'mean_wind_speed_kmh': 'Monthly mean wind speed (km/h)',
                               'mean_pressure_hPa': 'Monthly mean pressure (hPa)'}, inplace = True)
monthly_data.set_index("Year and month", inplace = True)

st.dataframe(monthly_data)

st.markdown("## Monthly data means in table")
# monthly_data_means.drop("date", axis = 1, inplace=True)
monthly_data_means.reset_index(inplace = True)
monthly_data_means.drop("date", axis = 1, inplace=True)
# monthly_data_means.rename(columns={"date": "Month"}, inplace=True)
monthly_data_means["Month"] = np.arange(1,13)
monthly_data_means.set_index("Month", inplace=True)
monthly_data_means = monthly_data_means.round(2)

monthly_data_means.rename(columns = {"mean_temp_out_deg": "Mean Temperature (°C)",
                                        "mean_high_temp_deg": "Mean of Max Temperatures (°C)",
                                        "mean_low_temp_deg": "Mean of Min Temperatures (°C)",
                                        "mean_rel_humidity_perc": "Mean Relative Humidity (%)",
                                        "mean_dewpoint_deg": "Mean Dewpoint Temperature (°C)",
                                        "mean_wind_speed_kmh": "Mean Wind Speed (km/h)",
                                        "mean_pressure_hPa": "Mean Sea Level Pressure (hPa)",
                                        "mean_pcp_acum_month_mm": "Mean Precipitation (mm)"}, inplace=True)
st.dataframe(monthly_data_means)