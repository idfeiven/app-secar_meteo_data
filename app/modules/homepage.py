import pandas as pd
import streamlit as st


def get_map_data():
    #Mostrar en un mapa la ubicación de la estación
    map_data = pd.DataFrame(
        [[39.6073994131482, 2.638403533715773]],
        columns=['lat', 'lon'])
    return map_data


# Título de la aplicación
st.title("Estación meteorológica Palma Secar de la Real")
st.write("Esta aplicación web muestra los datos de la estación\
        meteorológica ubicada en el barrio Palma Secar de la Real,\
        Mallorca. Modelo Davis Vantage Vue")

st.markdown("## Localización de la estación")
map_data = get_map_data()
st.map(map_data)