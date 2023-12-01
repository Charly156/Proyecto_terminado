##Importación de bibliotecas necesarias en la pagina de 'Analitico'##
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import calendar
import plotly.express as px

##Se asegura que el layout este en el formato wide##
st.set_page_config(layout='wide')

##Función para transformar el df a un archivo csv##
def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')

##Lectura de los archivos necesarios##
general = pd.read_excel('tabular_data_general.xlsx', index_col=0)
maternidad = pd.read_excel('tabular_data_maternidad.xlsx', index_col=0)
docentes = pd.read_excel('tabular_data_docentes.xlsx', index_col = 0)

##Título del dashboard##
st.title('Dashboard analítico')
st.markdown("***")

##Colocación de la imagen en el sidebar##
imagen = 'NetMX.png'
st.sidebar.image(imagen)

##Nueva columna 'Day' para especificar día de la semana##
general['Day'] = general['timestamp'].dt.day_name()
maternidad['Day'] = maternidad['timestamp'].dt.day_name()
docentes['Day'] = docentes['timestamp'].dt.day_name()

##Nueva columna 'Date' para identidicar la fecha##
general['Date'] = general['timestamp'].dt.date
maternidad['Date'] = maternidad['timestamp'].dt.date
docentes['Date'] = docentes['timestamp'].dt.date

##Nueva columna 'solo_outer' para determinar el valor del outer##
general['solo_outer'] = general['incoming_outer_count']-general['incoming_inner_count']
maternidad['solo_outer'] = maternidad['incoming_outer_count']-maternidad['incoming_inner_count']
docentes['solo_outer'] = docentes['incoming_outer_count']-docentes['incoming_inner_count']

##Creación de un nuevo DataFrame##
#Creación de una nueva columna usando 'total_visits' para uso posterior
general['General'] = general['total_visits']
maternidad['Maternidad'] = maternidad['total_visits']
docentes['Docentes'] = docentes['total_visits']
#Creación de nuevos valores
general['id_gen'] = general['sensor_id'] 
maternidad['id_mat'] = maternidad['sensor_id'] 
docentes['id_doc'] = docentes['sensor_id'] 
#Se agrupan las columnas 'timestamp', el 'total_group' de turno, y 'id_gen' por medio de 'timestamp', y 'id_gen'
flujo_general = general[['timestamp', 'General','id_gen']].groupby(['timestamp','id_gen']).sum().reset_index()
flujo_maternidad = maternidad[['timestamp','Maternidad','id_mat']].groupby(['timestamp','id_mat']).sum().reset_index()
flujo_docentes = docentes[['timestamp', 'Docentes','id_doc']].groupby(['timestamp','id_doc']).sum().reset_index()
#Se combinan las gráficas haciendo uso de merge para crear el nuevo DataFrame
flujo_gm = flujo_general.merge(flujo_maternidad, left_on = 'timestamp', right_on = 'timestamp')
flujo_sensores = flujo_gm.merge(flujo_docentes, left_on = 'timestamp', right_on = 'timestamp')
flujo_sensores['Day'] = flujo_sensores['timestamp'].dt.day_name()

##Creación del filtro del control de fechas dentro del sidebar##
#Creación de la fecha de inicio y la fecha final
st.sidebar.header('Control de fechas')
start_date = st.sidebar.date_input('Fecha de inicio', general['timestamp'].min())
end_date = st.sidebar.date_input('Fecha de fin', general['timestamp'].max())
#Convertir los datos a datetime64[ns]
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)
#Se crean los filtros para cada uno de los DataFrames existentes
general_filtrado = general[(general['timestamp'] >= start_date) & (general['timestamp'] <= end_date)]
#Verificar si la fecha inicial no es mayor que la final
if general_filtrado.empty :
    st.error("Error: Por favor seleccione las fechas de manera correcta.")
    st.stop()
maternidad_filtrado = maternidad[(maternidad['timestamp'] >= start_date) & (maternidad['timestamp'] <= end_date)]
docentes_filtrado = docentes[(docentes['timestamp'] >= start_date) & (docentes['timestamp'] <= end_date)]
flujo_filtrado = flujo_sensores[(flujo_sensores['timestamp'] >= start_date) & (flujo_sensores['timestamp'] <= end_date)]

##Creación de las dos columnas principales para el layout de la página de 'Analítico'##
col1, col2 = st.columns(2)
#Columna 1 principal. 
#Donde estaran el mapa, el gráfico de burbujas y el gráfico de línea.
with col1:
    ##Creación de las subcolumnas de la Columna 1 principal.##
    col1_1, col1_2 = st.columns(2)

    #Subcolumna 1 de la Columna 1 principal.
    #En esta subcolumna ubicada en la parte superior izquierda de la colunma, estara 
    #presente el mapa que ubicará a los sensores. 
    with col1_1:
        ##Creación del mapa que unicará a los sensores##
        # Cargar el archivo de Excel de las ubicaciones de los sensores en un DataFrame
        df = pd.read_excel("Ubicaciones.xlsx", index_col=0)
        st.subheader("Mapa de Sensores")
        # Slider para ajustar el nivel de zoom del mapa
        zoom_level = st.slider("Ajusta el nivel de zoom:", 1, 17, 5)
        # Crear un DataFrame con todas las ubicaciones
        map_data = pd.DataFrame({"latitude": df["sensor_latitude"], "longitude": df["sensor_longitude"]})
        # Mostrar el mapa
        st.map(map_data, zoom=zoom_level)

    #Subcolumna 2 de la Columna 1 principal.
    #En esta subcolumna ubicada en la parte superior derecha de la colunma, estara presente 
    #el diagrama de burbujas de la saturación promedio. 
    with col1_2:
        ##Creación del mapa de burbujas##
        st.subheader('Saturación promedio')
        #Se agrupan por medio del numero del sensor, y se saca el promedio de los 'total_visits'
        #respectivos
        sensores = flujo_filtrado.groupby(['id_gen', 'id_mat', 'id_doc'])[['General', 'Maternidad', 'Docentes']].mean().reset_index()
        #Se crea el gráfico de burbujas haciendo uso de pyplot.express
        fig = px.scatter(sensores, x='id_gen', y='General', size='General', size_max=max(sensores['General']))
        #Se agrega el gráfico pero con maternidad
        fig.add_trace(px.scatter(sensores, x='id_mat', y='Maternidad', size='Maternidad', 
                                 size_max=max(sensores['Maternidad'])).data[0])
        #Se agrega el gráfico pero con docentes
        fig.add_trace(px.scatter(sensores, x='id_doc', y='Docentes', size='Docentes', 
                                 size_max=max(sensores['Docentes'])).data[0])
        #Se visualiza el gráfico
        st.plotly_chart(fig, use_container_width=True, width=700)
    
    ##Creación del gráfico del flujo semanal en la parte inferior central de la columna 1##
    #Se establecen los números para los días de la semana para graficar correctamente
    dias_numeros = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 7}
    flujo_filtrado['day_number'] = flujo_filtrado['Day'].map(dias_numeros)
    #Se crea la gráfica usando pyplot.express
    st.subheader('Flujo semanal: 3 sensores')
    flujos = flujo_filtrado.groupby('day_number')[['General','Maternidad','Docentes']].sum().reset_index()
    flujos['Day'] = flujos['day_number'].apply(lambda x: calendar.day_name[x-1])
    fig = px.line(flujos, x='Day', y=['General','Maternidad','Docentes'])
    #Se visualiza el gráfico
    st.plotly_chart(fig, use_container_width=True)

##Columna 2 principal##
with col2:
    ##Creación de pestañas para las bases de datos##
    tab1, tab2, tab3 = st.tabs(['General', 'Maternidad', 'Docentes'])

    ##Pestaña con los datos de General##
    with tab1:
        #Se crean dos columnas para el grafico de barras y el de pie
        Gen1, Gen2 = st.columns(2)
        ##Parte superior izquierda de la columna 2 principal##
        with Gen1:
            ##Se crea el gráfico de barras con pyplot.express##
            st.subheader('Total de visitas')
            totalvisits_byday = general_filtrado.groupby('Day')['total_visits'].sum().reset_index()
            fig = px.bar(totalvisits_byday, x='Day', y='total_visits', 
                         category_orders={'Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                           'Saturday', 'Sunday']}, color = 'Day', color_continuous_scale='Viridis')
            #Se visualiza el gráfico
            st.plotly_chart(fig, use_container_width=True, width=700)

        ##Parte superior derecha de la columna 2 principal##
        with Gen2:
            ##Se crea el gráfico de pie con pyplot.express##
            st.subheader('Inner vs Outer')
            fig = px.pie(general_filtrado, 
                         values=general_filtrado[['incoming_inner_count','solo_outer']].sum(), 
                         names=general_filtrado[['incoming_inner_count','solo_outer']].sum().index, 
                         color = general_filtrado[['incoming_inner_count','solo_outer']].sum().index, 
                         color_discrete_sequence=px.colors.qualitative.Set1)
            #Se visualiza el gráfico
            st.plotly_chart(fig, use_container_width=True, width=700)
        
        ##Parte inferior central de la columna 2 principal##
        ##Se crea el gráfico de boxplot con pyplot.express##
        st.subheader('Visitas por día')
        fig = px.box(general_filtrado, x='Day', y='total_visits', 
                     category_orders={'Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                           'Saturday', 'Sunday']}, color='Day', color_discrete_sequence=px.colors.qualitative.Set1)
        #Se visualiza el gráfico
        st.plotly_chart(fig)

    ##Pestaña con los datos de Maternidad##
    with tab2:
        #Se crean dos columnas para el grafico de barras y el de pie
        Mat1, Mat2 = st.columns(2)

        ##Parte superior izquierda de la columna 2 principal##
        with Mat1:
            ##Se crea el gráfico de barras con pyplot.express##
            st.subheader('Total de visitas')
            totalvisits_byday = maternidad_filtrado.groupby('Day')['total_visits'].sum().reset_index()
            fig = px.bar(totalvisits_byday, x='Day', y='total_visits', 
                         category_orders={'Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                            'Saturday', 'Sunday']}, color = 'Day', color_continuous_scale='Viridis')
            #Se visualiza el gráfico
            st.plotly_chart(fig, use_container_width=True, width=700)
        
        ##Parte superior derecha de la columna 2 principal##
        with Mat2:
            ##Se crea el gráfico de pie con pyplot.express##
            st.subheader('Inner vs Outer')
            fig = px.pie(maternidad_filtrado, 
                         values=maternidad_filtrado[['incoming_inner_count','solo_outer']].sum(), 
                         names=maternidad_filtrado[['incoming_inner_count','solo_outer']].sum().index, 
                         color = maternidad_filtrado[['incoming_inner_count','solo_outer']].sum().index, 
                         color_discrete_sequence=px.colors.qualitative.Set1)
            st.plotly_chart(fig, use_container_width=True, width=700)

        ##Parte inferior central de la columna 2 principal##
        ##Se crea el gráfico de boxplot con pyplot.express##
        st.subheader('Visitas por día')
        fig = px.box(docentes_filtrado, x='Day', y='total_visits',
                      category_orders={'Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                           'Saturday', 'Sunday']}, color='Day', color_discrete_sequence=px.colors.qualitative.Set1)
        #Se visualiza el gráfico
        st.plotly_chart(fig)

    ##Pestaña con los datos de Docentes##
    with tab3:
        #Se crean dos columnas para el grafico de barras y el de pie
        Doc1, Doc2 = st.columns(2)

        ##Parte superior izquierda de la columna 2 principal##
        with Doc1:
            ##Se crea el gráfico de barras con pyplot.express##
            st.subheader('Total de visitas')
            fig, ax = plt.subplots()
            totalvisits_byday = docentes_filtrado.groupby('Day')['total_visits'].sum().reset_index()
            fig = px.bar(totalvisits_byday, x='Day', y='total_visits', 
                         category_orders={'Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                           'Saturday', 'Sunday']}, color = 'Day', color_continuous_scale='Viridis')
            #Se visualiza el gráfico
            st.plotly_chart(fig, use_container_width=True, width=700)
        
        ##Parte superior derecha de la columna 2 principal##
        with Doc2:
            ##Se crea el gráfico de pie con pyplot.express##
            st.subheader('Inner vs Outer')
            fig = px.pie(docentes_filtrado, 
                         values=docentes_filtrado[['incoming_inner_count','solo_outer']].sum(), 
                         names=docentes_filtrado[['incoming_inner_count','solo_outer']].sum().index, 
                         color = docentes_filtrado[['incoming_inner_count','solo_outer']].sum().index, 
                         color_discrete_sequence=px.colors.qualitative.Set1)
            #Se visualiza el gráfico
            st.plotly_chart(fig, use_container_width=True, width=700)

        ##Parte inferior central de la columna 2 principal##
        ##Se crea el gráfico de boxplot con pyplot.express##
        st.subheader('Visitas por día')
        fig = px.box(maternidad_filtrado, x='Day', y='total_visits', 
                     category_orders={'Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                           'Saturday', 'Sunday']}, color='Day', color_discrete_sequence=px.colors.qualitative.Set1)
        #Se visualiza el gráfico
        st.plotly_chart(fig)

##Creación del check box en el sidebar##
show_dt = st.sidebar.checkbox('Visualizar Tablas de datos', value = False)
#Lo que pasará una vez que el sidebar es seleccionado
if show_dt:
    #Usar st.dataframe para mostrar el DataFrame de General en Streamlit
    st.header('Datos General')
    st.dataframe(general)
    #Se usa la función para transformar el DataFrame en un archivo csv
    csv = convert_df(general)
    #Se crea el botón para descargar el DataFrame
    st.download_button(label="Download data as CSV", data=csv, file_name='general_data.csv', mime='text/csv')

    #Usar st.dataframe para mostrar el DataFrame de Docentes en Streamlit
    st.header('Datos Docentes')
    st.dataframe(docentes)
    #Se usa la función para transformar el DataFrame en un archivo csv
    csv = convert_df(docentes)
    #Se crea el botón para descargar el DataFrame
    st.download_button(label="Download data as CSV", data=csv, file_name='docentes_data.csv', mime='text/csv')

    #Usar st.dataframe para mostrar el DataFrame de Maternidad en Streamlit
    st.header('Datos Maternidad')
    st.dataframe(maternidad)
    #st.download_button('Descargar datos', data,'general_data.csv')
    csv = convert_df(maternidad)
    #Se crea el botón para descargar el DataFrame
    st.download_button(label="Download data as CSV", data=csv, file_name='maternidad_data.csv',mime='text/csv')