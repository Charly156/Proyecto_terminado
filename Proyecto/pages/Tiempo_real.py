##Importación de bibliotecas necesarias en la pagina de 'Tiempo_real'##
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

##Se asegura que el layout este en el formato wide##
st.set_page_config(layout='wide')

##Título del dashboard##
st.title('Dashboard de tiempo real')
st.markdown("***")

##Logo##
imagen = 'NetMX.png'
st.sidebar.image(imagen)

##Función para transformar el df a un archivo csv##
def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')

##Lectura de los archivos necesarios##
general = pd.read_excel('tabular_data_general.xlsx', index_col=0)
maternidad = pd.read_excel('tabular_data_maternidad.xlsx', index_col=0)
docentes = pd.read_excel('tabular_data_docentes.xlsx',index_col = 0)

##Nueva columna 'Hour' para especificar la hora en específico##
general['Hour'] = general['timestamp'].dt.hour
maternidad['Hour'] = maternidad['timestamp'].dt.hour
docentes['Hour'] = docentes['timestamp'].dt.hour

##Nueva columna 'solo_outer' para determinar el valor del outer##
general['solo_outer'] = general['incoming_outer_count']-general['incoming_inner_count']
maternidad['solo_outer'] = maternidad['incoming_outer_count']-maternidad['incoming_inner_count']
docentes['solo_outer'] = docentes['incoming_outer_count']-docentes['incoming_inner_count']

##Creación de pestañas para visualizar los dashboards de los distintos datos##
tab1, tab2, tab3 = st.tabs(['General', 'Maternidad', 'Docentes'])

##Pestaña de los datos de General##
with tab1:
    ##Filtro de una sola fecha##
    day_data_gen= general[((general['timestamp'].dt.year==2023) & (general['timestamp'].dt.month==8)&(general['timestamp'].dt.day==2))].copy()

    ##Creación de las columnas del dashboard de General##
    gen1, gen2, gen3 = st.columns(3)

    ##Columna 1. En esta estará presente la tasa de entradas y la gráfica de dona##
    with gen1:
        ##Cálculo de la tasa de entradas##
        st.subheader('Tasa de entradas')
        tasa = int(round((day_data_gen['incoming_inner_count'].sum()/day_data_gen['solo_outer'].sum())*100,))
        #Visualización de la métrica
        gen1.metric('',f'{tasa}%','')

        ##Creación del gráfico de donas con pyplot.express##
        st.subheader('Inner vs Outer')
        fig = px.pie(day_data_gen, 
                        values=day_data_gen[['incoming_inner_count','solo_outer']].sum(), 
                        names=day_data_gen[['incoming_inner_count','solo_outer']].sum().index,
                        hole = 0.5, color = day_data_gen[['incoming_inner_count','solo_outer']].sum().index, 
                        color_discrete_sequence=px.colors.qualitative.Set1)
        ##Visualización del gráfico##
        st.plotly_chart(fig, use_container_width=True)

    ##Columna 2. En esta estará presente el número de personas y la saturación actual##
    with gen2:
        ##Cálculo del número de personas##
        st.subheader('Número de personas')
        #Seleccionar última hora
        last_row=day_data_gen.iloc[-1]
        #Calcular total
        num_personas=int(last_row['total_visits'].sum())
        #Visualización de la métrica
        gen2.metric('',f'{num_personas}','')

        ##Cálculo de la saturación actual##
        st.subheader('Saturación actual')
        #Crear límites
        lim_s=general['total_visits'].mean() + np.std(general['total_visits'])
        lim_m=general['total_visits'].mean()
        lim_i=general['total_visits'].mean() - np.std(general['total_visits'])
        #-----------------------Visualizar datos--------------------------
        if day_data_gen['total_visits'].sum() > lim_s:
            st.markdown("<div style='text-align: center'><h2 style='color: blue'>Alta</h2></div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center'><h2 style='color: gray'>Media</h2></div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center'><h2 style='color: gray'>Baja</h2></div>", unsafe_allow_html=True)
        elif day_data_gen['total_visits'].sum() >= lim_i and day_data_gen['total_visits'].sum() <= lim_s:
            st.markdown("<div style='text-align: center'><h2 style='color: gray'>Alta</h2></div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center'><h2 style='color: blue'>Media</h2></div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center'><h2 style='color: gray'>Baja</h2></div>", unsafe_allow_html=True)
        elif day_data_gen['total_visits'].sum() < lim_i:
            st.markdown("<div style='text-align: center'><h2 style='color: gray'>Alta</h2></div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center'><h2 style='color: gray'>Media</h2></div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center'><h2 style='color: blue'>Baja</h2></div>", unsafe_allow_html=True)

    ##Columna 3. En esta estarán presentes las visitas acumuladas y el flujo por hora##
    with gen3:
        ##Cálculo del número de personas##
        st.subheader('Visitas acumuladas')
        # Calcular el total de visitas sumando la columna 'total_visits'
        total_visitas = int(day_data_gen['total_visits'].sum())
        #Visualización de la métrica
        gen3.metric('',f'{total_visitas}','')

        ##Creación del gráfico del flujo por hora con pyplot.express##
        st.subheader('Flujo por hora')
        horas = day_data_gen.groupby('Hour')['total_visits'].sum().reset_index()
        fig = px.line(horas, x='Hour', y= 'total_visits')
        #Visualización del gráfico
        st.plotly_chart(fig, use_container_width=True)

##Pestaña de los datos de Maternidad##
with tab2:
    ##Filtro de una sola fecha##
    day_data_mat= maternidad[((maternidad['timestamp'].dt.year==2023) & (maternidad['timestamp'].dt.month==8)&(maternidad['timestamp'].dt.day==2))].copy()
    
    ##Creación de las columnas del dashboard de Maternidad##
    mat1, mat2, mat3 = st.columns(3)

    ##Columna 1. En esta estará presente la tasa de entradas y la gráfica de dona##
    with mat1:
        ##Cálculo de la tasa de entradas##
        st.subheader('Tasa de entradas')
        tasa = int(round((day_data_mat['incoming_inner_count'].sum()/day_data_mat['solo_outer'].sum())*100,))
        #Visualización de la métrica
        mat1.metric('',f'{tasa}%','')

        ##Creación del gráfico de donas con pyplot.express##
        st.subheader('Inner vs Outer')
        fig = px.pie(day_data_mat, 
                        values=day_data_mat[['incoming_inner_count','solo_outer']].sum(), 
                        names=day_data_mat[['incoming_inner_count','solo_outer']].sum().index,
                        hole = 0.5, color = day_data_mat[['incoming_inner_count','solo_outer']].sum().index, 
                        color_discrete_sequence=px.colors.qualitative.Set1)
        #Visualización del gráfico
        st.plotly_chart(fig, use_container_width=True)

    with mat2:
        ##Cálculo del número de personas##
        st.subheader('Número de personas')
         #Seleccionar última hora
        last_row=day_data_mat.iloc[-1]
        #Calcular total
        num_personas=int(last_row['total_visits'].sum())
        #Visualización de la métrica
        mat2.metric('',f'{num_personas}','')

        ##Cálculo de la saturación actual##
        st.subheader('Saturación actual')
        #Crear límites
        lim_s=maternidad['total_visits'].mean() + np.std(general['total_visits'])
        lim_m=maternidad['total_visits'].mean()
        lim_i=maternidad['total_visits'].mean() - np.std(general['total_visits'])
        #-----------------------Visualizar datos--------------------------
        if day_data_mat['total_visits'].sum() > lim_s:
            st.markdown("<div style='text-align: center'><h2 style='color: blue'>Alta</h2></div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center'><h2 style='color: gray'>Media</h2></div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center'><h2 style='color: gray'>Baja</h2></div>", unsafe_allow_html=True)
        elif day_data_mat['total_visits'].sum() >= lim_i and day_data_mat['total_visits'].sum() <= lim_s:
            st.markdown("<div style='text-align: center'><h2 style='color: gray'>Alta</h2></div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center'><h2 style='color: blue'>Media</h2></div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center'><h2 style='color: gray'>Baja</h2></div>", unsafe_allow_html=True)
        elif day_data_mat['total_visits'].sum() < lim_i:
            st.markdown("<div style='text-align: center'><h2 style='color: gray'>Alta</h2></div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center'><h2 style='color: gray'>Media</h2></div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center'><h2 style='color: blue'>Baja</h2></div>", unsafe_allow_html=True)

    ##Columna 3. En esta estarán presentes las visitas acumuladas y el flujo por hora##
    with mat3:
        ##Cálculo del número de personas##
        st.subheader('Visitas acumuladas')
        # Calcular el total de visitas sumando la columna 'total_visits'
        total_visitas = int(day_data_mat['total_visits'].sum())
        #Visualización de la métrica
        mat3.metric('',f'{total_visitas}','')

        ##Creación del gráfico del flujo por hora con pyplot.express##
        st.subheader('Flujo por hora')
        horas = day_data_mat.groupby('Hour')['total_visits'].sum().reset_index()
        fig = px.line(horas, x='Hour', y= 'total_visits')
        #Visualización del gráfico
        st.plotly_chart(fig, use_container_width=True)

##Pestaña de los datos de Docentes##
with tab3:
    ##Filtro de una sola fecha##
    day_data_doc= docentes[((docentes['timestamp'].dt.year==2023) & (docentes['timestamp'].dt.month==8)&(docentes['timestamp'].dt.day==2))].copy()
    
    ##Creación de las columnas del dashboard de Docentes##
    doc1, doc2, doc3 = st.columns(3)

    ##Columna 1. En esta estará presente la tasa de entradas y la gráfica de dona##
    with doc1:
        ##Cálculo de la tasa de entradas##
        st.subheader('Tasa de entradas')
        tasa = int(round((day_data_doc['incoming_inner_count'].sum()/day_data_doc['solo_outer'].sum())*100,))
        #Visualización de la métrica
        doc1.metric('',f'{tasa}%','')

        ##Creación del gráfico de donas con pyplot.express##
        st.subheader('Inner vs Outer')
        fig = px.pie(day_data_doc, 
                        values=day_data_doc[['incoming_inner_count','solo_outer']].sum(), 
                        names=day_data_doc[['incoming_inner_count','solo_outer']].sum().index,
                        hole = 0.5, color = day_data_doc[['incoming_inner_count','solo_outer']].sum().index, 
                        color_discrete_sequence=px.colors.qualitative.Set1)
        #Visualización del gráfico
        st.plotly_chart(fig, use_container_width=True)

    with doc2:
        ##Cálculo del número de personas##
        st.subheader('Número de personas')
         #Seleccionar última hora
        last_row=day_data_doc.iloc[-1]
        #Calcular total
        num_personas=int(last_row['total_visits'].sum())
        #Visualización de la métrica
        doc2.metric('',f'{num_personas}','')

        ##Cálculo de la saturación actual##
        st.subheader('Saturación actual')
        #Crear límites
        lim_s=docentes['total_visits'].mean() + np.std(general['total_visits'])
        lim_m=docentes['total_visits'].mean()
        lim_i=docentes['total_visits'].mean() - np.std(general['total_visits'])
        #-----------------------Visualizar datos--------------------------
        if day_data_doc['total_visits'].sum() > lim_s:
            st.markdown("<div style='text-align: center'><h2 style='color: blue'>Alta</h2></div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center'><h2 style='color: gray'>Media</h2></div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center'><h2 style='color: gray'>Baja</h2></div>", unsafe_allow_html=True)
        elif day_data_doc['total_visits'].sum() >= lim_i and day_data_doc['total_visits'].sum() <= lim_s:
            st.markdown("<div style='text-align: center'><h2 style='color: gray'>Alta</h2></div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center'><h2 style='color: blue'>Media</h2></div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center'><h2 style='color: gray'>Baja</h2></div>", unsafe_allow_html=True)
        elif day_data_doc['total_visits'].sum() < lim_i:
            st.markdown("<div style='text-align: center'><h2 style='color: gray'>Alta</h2></div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center'><h2 style='color: gray'>Media</h2></div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center'><h2 style='color: blue'>Baja</h2></div>", unsafe_allow_html=True)

    ##Columna 3. En esta estarán presentes las visitas acumuladas y el flujo por hora##
    with doc3:
        ##Cálculo del número de personas##
        st.subheader('Visitas acumuladas')
        # Calcular el total de visitas sumando la columna 'total_visits'
        total_visitas = int(day_data_doc['total_visits'].sum())
        #Visualización de la métrica
        doc3.metric('',f'{total_visitas}','')

        ##Creación del gráfico del flujo por hora con pyplot.express##
        st.subheader('Flujo por hora')
        horas = day_data_doc.groupby('Hour')['total_visits'].sum().reset_index()
        fig = px.line(horas, x='Hour', y= 'total_visits')
        #Visualización del gráfico
        st.plotly_chart(fig, use_container_width=True)

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