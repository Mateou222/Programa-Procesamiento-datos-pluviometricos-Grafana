import os
import unicodedata
from datetime import datetime
import locale
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
from tkinter import *
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pyperclip
from PyQt5.QtGui import QIcon
from pyproj import CRS, Transformer
import matplotlib.image as mpimg

# Definir el sistema de coordenadas EPSG:4326 (Latitud/Longitud) y EPSG:32721 (UTM Zone 21S)
crs_4326 = CRS.from_epsg(4326)  # WGS 84 (Latitud, Longitud)
crs_32721 = CRS.from_epsg(32721)  # UTM Zone 21S

# Crear el transformador para convertir entre EPSG:4326 y EPSG:32721
transformer = Transformer.from_crs(crs_4326, crs_32721, always_xy=True)

# Variable global
duracion_tormenta = [10, 20, 30, 60, 120, 180, 360, 720, 1440]

# Valores de precipitación para cada periodo de retorno (TR)
precipitacion_tr = {
    "TR 2 años": [15.1, 19.8, 25.3, 33.4, 44.3, 51.4, 65.5, 80.5, 93.8],
    "TR 5 años": [19.4, 26.2, 33.37, 43.6, 57.2, 67.4, 85.9, 106.5, 124.6],
    "TR 10 años": [22.2, 30.4, 38.7, 50.3, 65.8, 78.0, 99.5, 123.7, 145.0],
    "TR 20 años": [24.9, 34.5, 43.9, 56.8, 74.0, 88.2, 112.5, 140.2, 164.6],
    "TR 25 años": [25.8, 35.8, 45.5, 58.8, 76.6, 91.4, 116.5, 145.5, 170.8],
    "TR 50 años": [28.5, 39.7, 50.6, 65.1, 84.6, 101.3, 129.3, 161.6, 189.9],
    "TR 100 años": [31.1, 43.7, 55.6, 71.3, 92.5, 111.2, 142.0, 177.6, 208.9]
}

precipitacion_tr_x_duracion = {
    "10 min": [15.1, 19.4, 22.2, 24.9, 25.8, 28.5, 31.1],
    "20 min": [19.8, 26.2, 30.4, 34.5, 35.8, 39.7, 43.7],
    "30 min": [25.3, 33.37, 38.7, 43.9, 45.5, 50.6, 55.6],
    "60 min": [33.4, 43.6, 50.3, 56.8, 58.8, 65.1, 71.3],
    "120 min": [44.3, 57.2, 65.8, 74.0, 76.6, 84.6, 92.5],
    "180 min": [51.4, 67.4, 78.0, 88.2, 91.4, 101.3, 111.2],
    "360 min": [65.5, 85.9, 99.5, 112.5, 116.5, 129.3, 142.0],
    "720 min": [80.5, 106.5, 123.7, 140.2, 145.5, 161.6, 177.6],
    "1440 min": [93.8, 124.6, 145.0, 164.6, 170.8, 189.9, 208.9]
}

tr_x_duracion = ["TR 2", "TR 5", "TR 10", "TR 20", "TR 25", "TR 50", "TR 100"]

def leer_archivo_principal(archivo):
    # Abro los archivos donde se encuentran las tablas con datos de grafana de pluviometros y depuro los datos
    
    # Aquí procesamos el archivo seleccionado
    df_datos = pd.read_csv(archivo, encoding="utf-8")
   
    # Convertir a datetime
    df_datos['Time'] = pd.to_datetime(df_datos['Time'])
    # Redondear a 5 minutos
    df_datos['Time'] = df_datos['Time'].dt.round('5min')
    
    # Agrupar por tiempo redondeado y consolidar valores
    df_datos = df_datos.groupby('Time').max()  # max() mantiene el valor no nulo más alto por grupo
    
    # Reindexar para asegurar intervalos completos de 5 minutos
    df_datos = df_datos.reindex(pd.date_range(start=df_datos.index.min(), 
                              end=df_datos.index.max(), 
                              freq='5min'))
    return df_datos

# Función para eliminar tildes
def eliminar_tildes(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn'
    )

def traducir_id_a_lugar(df_config, id_columna):
    # Buscar el lugar en el dataframe df_config donde la columna 'ID' tiene el valor id_columna
    lugar = df_config.loc[df_config['ID'] == id_columna, 'Lugar'].values
    
    # Si el lugar existe, retornarlo, si no, retornar None
    if lugar.size > 0:
        return lugar[0]
    else:
        return None  # Retorna None si no encuentra el ID en el dataframe
    
def traducir_lugar_a_id(df_config, lugar_columna):
    # Buscar el lugar en el dataframe df_config donde la columna 'ID' tiene el valor id_columna
    ID = df_config.loc[df_config['Lugar'] == lugar_columna, 'ID'].values
    
    # Si el lugar existe, retornarlo, si no, retornar None
    if ID.size > 0:
        return ID[0]
    else:
        return None  # Retorna None si no encuentra el ID en el dataframe

def traducir_columnas_lugar_a_id(df_config, df_acumulados_diarios):
    mapa_traduccion = dict(zip(df_config['Lugar'], df_config['ID']))
    
    df_acumulados_diarios.columns = [eliminar_tildes(col) for col in df_acumulados_diarios.columns]
    
    nuevas_columnas = [
        mapa_traduccion.get(col, col) if col != 'INUMET' else col 
        for col in df_acumulados_diarios.columns
    ]
    
    # Renombrar las columnas del dataframe
    df_acumulados_diarios.columns = nuevas_columnas
    
    return df_acumulados_diarios
    

def leer_archivo_verificador(archivo, df_datos):
    # Aquí procesamos el archivo seleccionado
    df_datos_validador = pd.read_csv(archivo, encoding="utf-8", sep=';', decimal=',')
    
    # Renombrar todas las columnas para evitar problemas de caracteres
    df_datos_validador.columns = (df_datos_validador.columns
                                  .str.normalize('NFKD')
                                  .str.encode('ascii', 'ignore')
                                  .str.decode('ascii')
                                  .str.replace(' ', '_')
                                  .str.lower())
    # Convertir a datetime
    df_datos_validador['fecha'] = pd.to_datetime(df_datos_validador['fecha'])
    # Redondear a 5 minutos
    df_datos_validador['fecha'] = df_datos_validador['fecha'].dt.round('5min')
    
    df_seleccionado = df_datos_validador[['fecha', 'precipitacion_-_valor_crudo']]
    
    # Agrupar por tiempo redondeado y consolidar valores
    df_seleccionado = df_seleccionado.groupby('fecha').max()  # max() mantiene el valor no nulo más alto por grupo
        
    # Cambiar el formato de la columna de fecha
    df_seleccionado.index = df_seleccionado.index.strftime('%Y-%m-%d %H:%M:%S')
    
    # Si hay valores faltantes, rellena hacia adelante
    df_seleccionado = df_seleccionado.bfill()
    
    df_datos.index = pd.to_datetime(df_datos.index)
    
    # Asegurarse de que los índices son de tipo datetime en ambos DataFrames
    df_seleccionado.index = pd.to_datetime(df_seleccionado.index, format='%Y-%m-%d %H:%M:%S', dayfirst=True, errors='coerce')
    
    
    # Filtrar df_seleccionado para que coincida con el rango de fechas de df_datos
    start_date = df_datos.index.min()
    end_date = df_datos.index.max()
    
    df_seleccionado = df_seleccionado[(df_seleccionado.index >= start_date) & (df_seleccionado.index <= end_date)]
    
    # Reindexado y alineación flexible por fecha más cercana
    df_seleccionado = df_seleccionado.reindex(df_datos.index, method='ffill')  # 'ffill' para llenar con el valor más cercano hacia adelante
    
# Agregar columna con nombre de la estación
    nombre_columna = df_datos_validador['estacion'].iloc[0]  # Obtener nombre de la estación
    nombre_columna = eliminar_tildes(nombre_columna)
    nombre_columna = nombre_columna.replace('Pluviometro - ', '').replace('Estacion Meteorologica - ', '')

    df_datos[nombre_columna] = df_seleccionado['precipitacion_-_valor_crudo']

    return df_datos

def leer_archivo_inumet(archivo, df_acumulados_diarios):    
    # Leer el archivo INUMET
    df_inumet = pd.read_csv(archivo, encoding="utf-8", sep=";")
    
    # Cambiar formato de fecha y establecer como índice
    df_inumet['FECHA'] = pd.to_datetime(df_inumet['FECHA'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')
    df_inumet.set_index('FECHA', inplace=True)
    
    # Asegurarse de que ambos DataFrames tengan índices compatibles
    df_acumulados_diarios.index = pd.to_datetime(df_acumulados_diarios.index).strftime('%Y-%m-%d')
    
    # Combinar ambos DataFrames por el índice
    df_acumulados_diarios = df_acumulados_diarios.join(df_inumet, how='left')
    
    # Opcional: Rellenar valores faltantes con 0
    df_acumulados_diarios.fillna(0, inplace=True)
    
    # Retornar el DataFrame combinado
    return df_acumulados_diarios

def acumulados(df_datos):
    # Crea un Dataframe con los acumulados por fecha y hora para cada pluviometro
    # Donde la diferencia es negativa, sumar el valor actual al acumulado anterior
    df_acumulados = df_datos.copy()

    for pluvio in df_datos.columns:
        df_acumulados[pluvio] = df_datos[pluvio].diff().apply(lambda x: x if x > 0 else 0).cumsum()
        
    return df_acumulados

def acumulado_total(acumulados):
    # Calcular el total acumulado para cada pluviómetro
    acumulado_total = acumulados.max()
    acumulado_total.name = 'Total'  # Asignamos el nombre 'Total'
    
    return acumulado_total.to_frame().T  # Convertimos el Series a DataFrame

def acumulado_diarios_total(df_acumulados_diarios):
    df = df_acumulados_diarios.copy()
     # Calcular la suma de las filas para cada columna
    suma_total = df.sum(axis=0)
    
    # Añadir la suma como nueva fila al final del dataframe
    df.loc['Total'] = suma_total
    
    return df

def calcular_instantaneos(df_datos):
    # Crea un Dataframe con los valores instantaneos por fecha y hora para cada pluviometro

    # Calcular el valor instantáneo (diferencias)
    df_datos = df_datos.diff()

    # Eliminar valores negativos (reinicios)
    df_datos = df_datos.map(lambda x: x if x > 0 else 0)
    return df_datos

    