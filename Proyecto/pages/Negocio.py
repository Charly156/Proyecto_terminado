##Importación de bibliotecas necesarias en la pagina de 'Negocio'##
import streamlit as st
import folium
from folium.plugins import HeatMap
import numpy as np
import pandas as pd
import math
import plotly.express as px
from streamlit_folium import folium_static

##Se asegura que el layout este en el formato wide##
st.set_page_config(layout='wide')

##Título del dashboard##
st.title('Dashboard de negocio')
st.markdown("***")

##Logo##
imagen = 'NetMX.png'
st.sidebar.image(imagen)

##Lectura de los archivos necesarios##
df = pd.read_excel('nuevo_archivo.xlsx')
df_general = pd.read_excel('tabular_data_general.xlsx', index_col=0)

##Función para transformar el df a un archivo csv##
def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')

##Función para la creación de grafico scatter para más adelante##
def fx(x, angle, sigma):
    tangent = math.tan(np.deg2rad(angle))
    y = abs(tangent*x+np.random.normal(0.0, sigma))
    return y
angle = 45
sigma = 5
#Columna de basura por sensor con error
df_general['basura']=df_general.apply(lambda row:fx(row['total_visits'],angle,sigma),axis=1)
#Columna de basura por sensor sin error
df_general['basura_0']=fx(df_general['total_visits'],angle,0)

##Nueva columna Day##
df['Day'] = df['timestamp'].dt.day_name()

##Creación del filtro del control de fechas dentro del sidebar##
#Creación de la fecha de inicio y la fecha final
st.sidebar.header('Control de fechas')
start_date = st.sidebar.date_input('Fecha de inicio', df['timestamp'].min())
end_date = st.sidebar.date_input('Fecha de fin', df['timestamp'].max())
#Convertir objetos a datetime64[ns]
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)
#Se crean los filtros para cada uno de los DataFrames existentes
df_filtrado = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
#Verificar si la fecha inicial no es mayor que la final
if df_filtrado.empty :
    st.error("Error: Por favor seleccione las fechas de manera correcta.")
    st.stop()
general_filtrado = df_general[(df_general['timestamp'] >= start_date) & (df_general['timestamp'] <= end_date)]

##Creación de dos columnas principales para la distribución del layout##
col1, col2 = st.columns(2)

##Columna principal 1##
with col1:
    ##Creación de dos subcolumnas dentro de la columna principal 1##
    col1_1, col1_2 = st.columns(2)

    ##Parte superior izquierda de la columna principal 1##
    with col1_1:
        ##Creación del gráfico de barras con pyplot.express##
        st.subheader('Personas que se subieron a los juegos en la semana')
        totalvisits_byday = df_filtrado.groupby('Day')['total_visits'].sum().reset_index()
        fig = px.bar(totalvisits_byday, x='Day', y='total_visits', 
                        category_orders={'Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                        'Saturday', 'Sunday']}, color = 'Day', color_continuous_scale='Viridis')
        #Visualización del gráfico
        st.plotly_chart(fig, use_container_width=True, width=700)

    ##Parte superior derecha de la columna principal 1##
    with col1_2:
        ##Creación del gráfico de scatter y linea con pyplot.express##
        st.subheader("Total de visitas VS basura")
        fig = px.scatter(general_filtrado, x="total_visits", y="basura", 
                         labels={"basura": "Basura", "total_visits": "Total de Visitas"})
        fig.add_scatter(x=general_filtrado["total_visits"], y=general_filtrado["basura_0"], 
                        mode='lines', line=dict(color='green'), name="Línea Verde")
        #Visualización del gráfico
        st.plotly_chart(fig, use_container_width=True, width=700)

    ##Parte inferior central de la columna principal 1##
    ##Creación del mapa de calor pyplot.express##
    st.subheader('Visitas por juego')
    #Convierte la columna 'timestamp' a tipo datetime
    df_filtrado['timestamp'] = pd.to_datetime(df_filtrado['timestamp'])
    #Agrega una columna con el nombre del mes
    df_filtrado['nombre_mes'] = df_filtrado['timestamp'].dt.strftime('%B')  # %B devuelve el nombre completo del mes
    #Define el orden de los meses disponibles
    order_of_months = ['August', 'September', 'October']
    df_filtrado['nombre_mes'] = pd.Categorical(df_filtrado['nombre_mes'], categories=order_of_months, ordered=True)
    #Agrupa los datos por sensor y mes, calculando el total de visitas por mes
    df_monthly = df_filtrado.groupby(['sensor_id', 'nombre_mes'])['total_visits'].sum().reset_index()
    #Código para la visualización de datos
    #Crea la gráfica de calor horizontal con Plotly Express
    heatmap_data = df_monthly.pivot(index='sensor_id', columns='nombre_mes', values='total_visits')
    fig = px.imshow(heatmap_data,
                    labels=dict(x="Nombre del Mes", y="Sensor ID", color="Total de Visitas"),
                    x=heatmap_data.columns,
                    y=heatmap_data.index,
                    color_continuous_scale="viridis",
                    color_continuous_midpoint=heatmap_data.values.mean())
    #Visualización del gráfico
    st.plotly_chart(fig)

##Columna principal 2##
with col2:
    ##Parte superior de la columna principal 2##
    ##Creación del gráfico de barras con pyplot.express##
    st.subheader('Personas que se subieron a cada juego')
    totalvisits_byday = df_filtrado.groupby('sensor_id')['total_visits'].sum().reset_index()
    fig = px.bar(totalvisits_byday, x='sensor_id', y='total_visits', color = 'sensor_id', 
                 color_continuous_scale='Viridis')
    #Visualización del gráfico
    st.plotly_chart(fig, use_container_width=True, width=700)

    ##Parte inferior de la columna principal 2##
    ##Creación de mapa de saturación##
    st.subheader('Saturación actual por juego')
    #Agrupa los datos por sensor y ubicación, y suma los total_visits
    sensor_data = df_filtrado.groupby(['sensor_id', 'Latitude','Longitude']).agg({'total_visits': 'sum'}).reset_index()
    #Crear un DataFrame con todas las ubicaciones
    map_data = pd.DataFrame({"latitude": sensor_data["Latitude"], "longitude": sensor_data["Longitude"],
        "total_visits": sensor_data["total_visits"]})
    #Crear un mapa con Folium
    mapa = folium.Map(location=[sensor_data['Latitude'].mean(), sensor_data['Longitude'].mean()])
    #Agregar un mapa de calor con los datos de total_visits
    HeatMap(data=map_data[['latitude', 'longitude', 'total_visits']], radius=15).add_to(mapa)
    #Mostrar el mapa en Streamlit
    folium_static(mapa)

##Creación del check box en el sidebar##
show_dt = st.sidebar.checkbox('Visualizar Tablas de datos', value = False)
#Lo que pasará una vez que el sidebar es seleccionado
if show_dt:
    #Usar st.dataframe para mostrar el DataFrame de General en Streamlit
    st.header('Datos General')
    st.dataframe(df_general)
    #Se usa la función para transformar el DataFrame en un archivo csv
    csv = convert_df(df_general)
    #Se crea el botón para descargar el DataFrame
    st.download_button(label="Download data as CSV", data=csv, file_name='general_data.csv', mime='text/csv')

    #Usar st.dataframe para mostrar el DataFrame de las atracciones en Streamlit
    st.header('Datos de las atracciones')
    st.dataframe(df)
    #Se usa la función para transformar el DataFrame en un archivo csv
    csv = convert_df(df)
    #Se crea el botón para descargar el DataFrame
    st.download_button(label="Download data as CSV", data=csv, file_name='Atracciones_data.csv', mime='text/csv')