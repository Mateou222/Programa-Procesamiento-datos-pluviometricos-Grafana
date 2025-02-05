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
from pyproj import CRS, Transformer
import matplotlib.image as mpimg
from PIL import Image, ImageTk
from datetime import time
import openpyxl

# Definir el sistema de coordenadas EPSG:4326 (Latitud/Longitud) y EPSG:32721 (UTM Zone 21S)
crs_4326 = CRS.from_epsg(4326)  # WGS 84 (Latitud, Longitud)
crs_32721 = CRS.from_epsg(32721)  # UTM Zone 21S

# Crear el transformador para convertir entre EPSG:4326 y EPSG:32721
transformer = Transformer.from_crs(crs_4326, crs_32721, always_xy=True)

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
    """
    Lee un archivo CSV con datos de precipitación, realiza ajustes en las fechas y las redondea a intervalos de 5 minutos.
    
    Parámetros:
    - archivo: Ruta del archivo CSV con los datos.
    
    Retorna:
    - DataFrame con los datos agrupados por fecha redondeada a 5 minutos.
    """
    df_datos = pd.read_csv(archivo, encoding="utf-8")
   
    df_datos['Time'] = pd.to_datetime(df_datos['Time'])
    # Redondear a 5 minutos
    df_datos['Time'] = df_datos['Time'].dt.round('5min')
    
    df_datos = df_datos.groupby('Time').max()  # max() mantiene el valor no nulo más alto por grupo
    
    # Reindexar para asegurar intervalos completos de 5 minutos
    df_datos = df_datos.reindex(pd.date_range(start=df_datos.index.min(), 
                              end=df_datos.index.max(), 
                              freq='5min'))
    return df_datos

def eliminar_tildes(texto):
    """
    Elimina los acentos de un texto.
    
    Parámetros:
    - texto: Cadena de texto con posibles acentos.
    
    Retorna:
    - Cadena de texto sin acentos.
    """
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn'
    )

def traducir_id_a_lugar(df_config, id_columna):
    lugar = df_config.loc[df_config['ID'] == id_columna, 'Lugar'].values
    
    if lugar.size > 0:
        return lugar[0]
    else:
        return None  
    
def traducir_lugar_a_id(df_config, lugar_columna):
    """
    Traduce un ID de lugar a su nombre de lugar correspondiente.
    
    Parámetros:
    - df_config: DataFrame con la configuración de lugares e IDs.
    - id_columna: ID de la columna que se desea traducir.
    
    Retorna:
    - Nombre del lugar correspondiente al ID, o None si no se encuentra.
    """
    ID = df_config.loc[df_config['Lugar'] == lugar_columna, 'ID'].values
    
    if ID.size > 0:
        return ID[0]
    else:
        return None 

def traducir_columnas_lugar_a_id(df_config, df_acumulados_diarios):
    """
    Traduce el nombre de un lugar a su ID correspondiente.
    
    Parámetros:
    - df_config: DataFrame con la configuración de lugares e IDs.
    - lugar_columna: Nombre del lugar que se desea traducir.
    
    Retorna:
    - ID correspondiente al nombre del lugar, o None si no se encuentra.
    """
    mapa_traduccion = dict(zip(df_config['Lugar'], df_config['ID']))
    
    df_acumulados_diarios.columns = [eliminar_tildes(col) for col in df_acumulados_diarios.columns]
    
    nuevas_columnas = [
        mapa_traduccion.get(col, col) if col != 'INUMET' else col 
        for col in df_acumulados_diarios.columns
    ]
    
    df_acumulados_diarios.columns = nuevas_columnas
    
    return df_acumulados_diarios
    

def leer_archivo_verificador(archivo, df_datos):
    """
    Lee el archivo de validación de datos, realiza las transformaciones necesarias y agrega la columna de precipitaciones crudas.
    
    Parámetros:
    - archivo: Ruta del archivo CSV con los datos de verificación.
    - df_datos: DataFrame con los datos existentes a los que se agregará la columna de precipitaciones crudas.
    
    Retorna:
    - DataFrame con la columna de precipitaciones crudas añadida.
    """
    df_datos_validador = pd.read_csv(archivo, encoding="utf-8", sep=';', decimal=',')
    
    # Renombrar todas las columnas para evitar problemas de caracteres
    df_datos_validador.columns = (df_datos_validador.columns
                                  .str.normalize('NFKD')
                                  .str.encode('ascii', 'ignore')
                                  .str.decode('ascii')
                                  .str.replace(' ', '_')
                                  .str.lower())
    df_datos_validador['fecha'] = pd.to_datetime(df_datos_validador['fecha'])
    df_datos_validador['fecha'] = df_datos_validador['fecha'].dt.round('5min')
        
    df_seleccionado = df_datos_validador[['fecha', 'precipitacion_-_valor_manual']].copy()
        
    df_seleccionado['precipitacion_-_valor_manual'] = df_seleccionado['precipitacion_-_valor_manual'].fillna(0)
        
    df_seleccionado = df_seleccionado.groupby('fecha').max()  # max() mantiene el valor no nulo más alto por grupo
        
    df_seleccionado.index = df_seleccionado.index.strftime('%Y-%m-%d %H:%M:%S')
    
    
    df_datos.index = pd.to_datetime(df_datos.index)
    
    df_seleccionado.index = pd.to_datetime(df_seleccionado.index, format='%Y-%m-%d %H:%M:%S', dayfirst=True, errors='coerce')
    
    start_date = df_datos.index.min()
    end_date = df_datos.index.max()
    
    df_seleccionado = df_seleccionado[(df_seleccionado.index >= start_date) & (df_seleccionado.index <= end_date)]
    
    df_seleccionado = df_seleccionado.reindex(df_datos.index, method='ffill')  
    
    # Agregar columna con nombre de la estación
    nombre_columna = df_datos_validador['estacion'].iloc[0]  
    nombre_columna = eliminar_tildes(nombre_columna)
    nombre_columna = nombre_columna.replace('Pluviometro - ', '').replace('Estacion Meteorologica - ', '')

    df_datos[nombre_columna] = df_seleccionado['precipitacion_-_valor_manual']

    return df_datos

def leer_archivo_inumet(archivo):   
    """
    Lee el archivo de INUMET en formato CSV o Excel y lo devuelve como un DataFrame.

    Parámetros:
    - archivo: Ruta del archivo (puede ser .csv, .xlsx o .xls).

    Retorna:
    - DataFrame con los datos de INUMET.
    """ 
    # Verificar si el archivo es CSV o Excel
    if archivo.endswith('.csv'):
        df_inumet = pd.read_csv(archivo, encoding="utf-8", sep=";")
    elif archivo.endswith('.xlsx') or archivo.endswith('.xls'):
        df_inumet = pd.read_excel(archivo, engine='openpyxl')  # Usa 'openpyxl' para archivos .xlsx
    else:
        raise ValueError("Formato de archivo no soportado. Usa CSV o Excel (.xlsx, .xls).")
    
    # Convertir la columna de fecha a formato estándar
    df_inumet['FECHA'] = pd.to_datetime(df_inumet['FECHA'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')
    df_inumet.set_index('FECHA', inplace=True)
    
    return df_inumet

def acumulados(df_datos):
    """
    Calcula los acumulados de precipitaciones a partir de los datos, asegurando que solo se sumen valores positivos.
    
    Parámetros:
    - df_datos: DataFrame con los datos de precipitación.
    
    Retorna:
    - DataFrame con los acumulados.
    """
    df_acumulados = df_datos.copy()

    for pluvio in df_datos.columns:
        df_acumulados[pluvio] = df_datos[pluvio].diff().apply(lambda x: x if x > 0 else 0).cumsum()
        
    return df_acumulados

def acumulado_total(acumulados):
    """
    Calcula el total acumulado para cada columna (pluviómetro).
    
    Parámetros:
    - acumulados: DataFrame con los acumulados de precipitación.
    
    Retorna:
    - DataFrame con el total acumulado por pluviómetro.
    """ 
    acumulado_total = acumulados.max()
    acumulado_total.name = 'Total'  
    
    return acumulado_total.to_frame().T  

def acumulado_diarios_total(df_acumulados_diarios):
    """
    Calcula el total acumulado por día para cada estación.
    
    Parámetros:
    - df_acumulados_diarios: DataFrame con los acumulados diarios.
    
    Retorna:
    - DataFrame con los totales por día y la fila 'Total'.
    """
    df = df_acumulados_diarios.copy()
    suma_total = df.sum(axis=0)
    
    df.loc['Total'] = suma_total
    
    return df

def calcular_instantaneos(df_datos):
    """
    Calcula las precipitaciones instantáneas (diferencia entre mediciones consecutivas).
    
    Parámetros:
    - df_datos: DataFrame con los datos de precipitación.
    
    Retorna:
    - DataFrame con las precipitaciones instantáneas.
    """
    df_datos = df_datos.diff()

    df_datos = df_datos.map(lambda x: x if x > 0 else 0)
    return df_datos




