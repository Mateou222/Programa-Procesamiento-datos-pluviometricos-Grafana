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

# Crear o cargar el dataframe con las configuraciones
def cargar_config():
    if os.path.exists('configuraciones.csv'):
        df_config = pd.read_csv('configuraciones.csv', encoding="utf-8")
    else:
        # Si no existe el archivo, crear un dataframe vacío con las columnas esperadas
        df_config = pd.DataFrame(columns=['Lugar', 'ID'])
    df_config["Lugar"] = df_config["Lugar"].apply(eliminar_tildes)
    
    return df_config

# Guardar el dataframe
def guardar_config(df_config):
    df_config.to_csv('configuraciones.csv', index=False, encoding='utf-8')

# Función para agregar nuevos lugares y columnas a la configuración
def agregar_equipos_nuevos_config(df_config, df_datos):
    # Eliminar tildes en los nombres de las columnas de df_datos
    df_datos.columns = [eliminar_tildes(col) for col in df_datos.columns]
    
    # Agregar nuevos lugares que no estén en df_config (solo en las filas)
    for col in df_datos.columns:
        # Verificar si el "lugar" (nombre de la columna) ya existe en df_config como fila
        if col not in df_config['Lugar'].values:
            # Crear una nueva fila con el "lugar" y un ID vacío o el valor correspondiente
            new_row = pd.DataFrame({'Lugar': [col], 'ID': [None]})
            df_config = pd.concat([df_config, new_row], ignore_index=True)

    return df_config

# Función para eliminar lugares que no están en df_datos
def eliminar_lugares_no_existentes_config(df_config, df_datos):
    # Obtener los lugares de df_config que no están en las columnas de df_datos
    lugares_existentes = df_datos.columns
    df_config = df_config[df_config['Lugar'].isin(lugares_existentes)]
    return df_config

def detectar_id_faltante_config(df_config):
    # Filtrar las filas donde el valor de 'ID' es nulo (None o NaN)
    lugares_faltantes_id = df_config[df_config['ID'].isna()]['Lugar'].tolist()
    return lugares_faltantes_id

# Función para actualizar los nombres de las columnas de df_datos
def actualizar_columnas_datos_config(df_config, df_datos):
    # Iterar sobre las filas de df_config
    for _, row in df_config.iterrows():
        lugar = row['Lugar']
        nuevo_id = row['ID']
        
        # Verificar si el lugar está en las columnas de df_datos
        if lugar in df_datos.columns:
            # Renombrar la columna correspondiente al lugar por el ID
            df_datos = df_datos.rename(columns={lugar: nuevo_id})
    
    return df_datos

def traducir_id_a_lugar(df_config, id_columna):
    # Buscar el lugar en el dataframe df_config donde la columna 'ID' tiene el valor id_columna
    lugar = df_config.loc[df_config['ID'] == id_columna, 'Lugar'].values
    
    # Si el lugar existe, retornarlo, si no, retornar None
    if lugar.size > 0:
        return lugar[0]
    else:
        return None  # Retorna None si no encuentra el ID en el dataframe

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

def calcular_instantaneos(df_datos):
    # Crea un Dataframe con los valores instantaneos por fecha y hora para cada pluviometro

    # Calcular el valor instantáneo (diferencias)
    df_datos = df_datos.diff()

    # Eliminar valores negativos (reinicios)
    df_datos = df_datos.map(lambda x: x if x > 0 else 0)
    return df_datos
