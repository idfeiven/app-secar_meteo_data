import datetime
import streamlit as st
from common import load_daily_data,\
                   plot_interactive_current,\
                   plot_static_current,\
                   select_column_box,\
                   get_df_variable_description


def filter_current_data(data):
    data_current = data[data.index.year == datetime.datetime.now().year]
    return data_current


st.markdown("# Recent data")
st.write(
    """In this page you can inspect weather data of the last 30 days."""
)

data = load_daily_data()
data_current = filter_current_data(data)
column = select_column_box(data, key = "pcp (mm)")

plot_interactive_current(data_current, column)
plot_static_current(data_current, column)

#Añadir descripción de variables
st.write("Variable description")
df_var_descr = get_df_variable_description(data)
df_var_descr