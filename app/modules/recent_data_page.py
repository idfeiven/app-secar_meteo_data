import datetime
import streamlit as st
from common import load_daily_data,\
                   plot_interactive_current,\
                   select_column_box,\
                   get_dict_rename_cols


def filter_current_data(data):
    data_current = data[data.index.year == datetime.datetime.now().year]
    return data_current

set_page_config = st.set_page_config(
    page_title="Datos recientes",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("# Datos recientes")
st.write(
    """En esta página puedes inspeccionar los datos meteorológicos de los últimos 30 días."""
)

data = load_daily_data()
data.rename(columns = get_dict_rename_cols(), inplace=True)
data_current = filter_current_data(data)
column = select_column_box(data, key = data.columns[0])

plot_interactive_current(data_current, column)