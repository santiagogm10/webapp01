import streamlit as st
import pandas as pd
import numpy as np
from math import sqrt
import time

def func_entrada_datos():
    num_fondos = int(st.text_input(f"Ingrese la Cantidad de Fondos a Simular ", 0))

    portafolios_seleccionados = []
    # Insertar funcion para tener una lista de portafolios a partir de una tabla en BD
    portafolios = ['CREDICORP CAPITAL ACCIONES COLOMBIA', 'CREDICORP CAPITAL ACCIONES GLOBALES', 'CREDICORP CAPITAL ACCIONES LATAM', 
                'CREDICORP CAPITAL DEUDA CORPORATIVA', 'CREDICORP CAPITAL DOLAR EFECTIVO']
    Lista_a_totalizar = []
    Total = 0

    for i in range(0,num_fondos):

        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
        portafolio_elegible = st.selectbox(f"Ingrese el Fondo # {i+1}", ([item for item in portafolios if item not in portafolios_seleccionados]))
        portafolios_seleccionados.append(portafolio_elegible)

        monto_a_invertir = int(st.text_input(f"Ingrese el monto del Fondo # {i+1}",0))
        
        Lista_a_totalizar.append(monto_a_invertir)
        Total = sum(Lista_a_totalizar)
        st.divider()

    datos = {
        'Fondo': portafolios_seleccionados,
        'Valores': Lista_a_totalizar
    }

    df = pd.DataFrame(datos)
    df['porc'] = df['Valores']/Total
    # df['porc'] = df['porc'].map(lambda x: '{:.2%}'.format(x)) # Se comenta para poder realizar las operaciones

    st.write(f"El Total a invertir en los Fondos es: {Total}")
    return df


def calc_var_y_volat(path:str):

    st.write("### CÁLCULO DE INDICADORES")
    #path = "C:/Users/santiago.gomez_bluet/Documents/SGM/Proyectos/CrediCorp/Calculadora Portafolio Modelo/calculadorahastavector/Archivos Pruebas"
    df_matriz = pd.read_excel(f'{path}/Matriz_Var_Covarianza.xlsx')
    df_participaciones = pd.read_excel(f'{path}/Participaciones.xlsx')
    df_rent_esperada = pd.read_excel(f'{path}/Rentabilidad_Esperada.xlsx')
    df_dim_FIC_SubTipoActivo = pd.read_excel(f'{path}/Participacion_FIC_SubTipoActivo.xlsx')

    # Se toman solo los valores numericos de la matriz y se convierte a arreglos
    df_matriz_conv = df_matriz.iloc[:, 2:]
    matriz_numpy = df_matriz_conv.to_numpy()

    # Calculo de la Varianza y Voltatilidad con productos entre matrices
    arr_participaciones = np.array(df_participaciones['Participaciones BP 100'])
    shape = arr_participaciones.shape

    pos_1 = shape[0]
    try:
        pos_2 = shape[1]
    except:
        pos_2 = 1

    arr_participaciones_T = arr_participaciones.reshape(pos_2,pos_1)

    prod_mat_1 =  np.matmul(arr_participaciones_T, matriz_numpy)
    prod_mat_2 = np.matmul(prod_mat_1, arr_participaciones)

    Varianza = float(prod_mat_2)
    Volatilidad = sqrt(Varianza)

    st.write(f" La Volatilidad es: {Volatilidad:.2%}")
    st.write("  La Varianza es: ", Varianza)

    # Se les asigna de nuevo las dimensiones para asegurar el tamaño de las matrices
    arr_participaciones = arr_participaciones.reshape(pos_1,pos_2)
    arr_rent_esperada = np.array(df_rent_esperada['Rentabilidad Esperada LP']).reshape(pos_1,pos_2)

    # Calculo de la Rentabilidad Esperada
    rentabilidad_esperada = np.dot(arr_participaciones.T, arr_rent_esperada)
    rentabilidad_esperada = float(rentabilidad_esperada[0,0])

    #print(f"La Rentabilidad Esperada es: {rentabilidad_esperada:.2%}")
    st.write(f" La Rentabilidad Esperada es: {rentabilidad_esperada:.2%}")
    return df_dim_FIC_SubTipoActivo


def calc_vector_pos(df, df_dim_FIC_SubTipoActivo):
    df['Nombre_Fondo'] = df['Fondo']
    del df['Fondo']

    df_datos_join = pd.merge(df, df_dim_FIC_SubTipoActivo ,  on='Nombre_Fondo', how='left')

    df_datos_join['porc'] = df_datos_join['porc'].astype(float)
    df_datos_join['Factor_participacion'] = df_datos_join['Factor_participacion'].astype(float)

    df_datos_join['Producto'] = df_datos_join['porc'] * df_datos_join['Factor_participacion']

    # st.dataframe(data=df_datos_join)
    st.write("### VECTOR DE POSICIONAMIENTO")

    df_vec_pos = df_datos_join
    # Se eliminan las columnas que no se necesitan
    del df_vec_pos['Valores']
    del df_vec_pos['porc']
    del df_vec_pos['codigo_fondo']
    del df_vec_pos['Nombre_Fondo']
    del df_vec_pos['Factor_participacion']

    # Dataframe con la columna Nombre_Sub_Tipo_Activo
    # st.dataframe(data=df_vec_pos)

    df_vec_pos_2 = df_vec_pos.groupby('Codigo_SubTipo_Activo')['Producto'].sum().reset_index()
    df_vec_pos_2['Producto'] = df_vec_pos_2['Producto'].map(lambda x: '{:.2%}'.format(x))

    # Dataframe con el Codigo_Sub_Tipo_Activo y %
    st.dataframe(data=df_vec_pos_2)




with st.sidebar:
    with st.echo():
        "Barra Lateral"

with st.container():
    st.markdown("<h1 style='text-align: center;'>Calculadora de Fondos V2</h1>", unsafe_allow_html=True)

#st.write(""" ## Paso 0 - Entrada de Datos """)

with st.container(border=True):
# Entrada de Datos
    col1, col2 = st.columns(2)
    
    with col1:
        df = func_entrada_datos()

    with col2:
        # Calculo de Varianza y Volatilidad
        # Ingresar la ruta donde se encuentran los archivos Matriz, Participaciones y demás
        st.write("COLUMNA 2 ")
        # df_dim_FIC_SubTipoActivo = calc_var_y_volat("C:/Users/santiago.gomez_bluet/Documents/SGM/Proyectos/CrediCorp/Calculadora Portafolio Modelo/calculadorahastavector/Archivos Pruebas")

        # Calculo del Vector de Posicionamiento
        # calc_vector_pos(df, df_dim_FIC_SubTipoActivo)
