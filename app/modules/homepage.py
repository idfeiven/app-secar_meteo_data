import pandas as pd
import streamlit as st


def _get_map_data():
    #Mostrar en un mapa la ubicación de la estación
    map_data = pd.DataFrame(
        [[39.6073994131482, 2.638403533715773]],
        columns=['lat', 'lon'])
    return map_data


# Título de la aplicación
st.title("Palma Secar de la Real weather data")

st.write("In this web app you can find my weather station data\
        located in Palma Secar de la Real neighborhood, Mallorca")

st.markdown("## Station location")
map_data = _get_map_data()
st.map(map_data)