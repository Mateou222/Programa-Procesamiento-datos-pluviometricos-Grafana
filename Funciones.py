from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter, HourLocator, MinuteLocator
import pandas as pd
import datetime as dt
import numpy as np
import os
import matplotlib.dates as mdates


def leer_archivo(archivo):
    # TODO: Abro los archivos donde se encuentran las tablas con datos de grafana de pluviometros y depuro los datos
    
    # Aquí procesamos el archivo seleccionado
    datos = pd.read_csv(archivo, encoding="utf-8")
   
    # Convertir a datetime
    datos['Time'] = pd.to_datetime(datos['Time'])
    # Redondear a 5 minutos
    datos['Time'] = datos['Time'].dt.round('5min')
    
    # Agrupar por tiempo redondeado y consolidar valores
    datos = datos.groupby('Time').max()  # max() mantiene el valor no nulo más alto por grupo
    
    # Reindexar para asegurar intervalos completos de 5 minutos
    datos = datos.reindex(pd.date_range(start=datos.index.min(), 
                              end=datos.index.max(), 
                              freq='5min'))
    
    return datos

def obtener_pluviometros_validos(datos):
    """Devuelve los nombres de los pluviómetros con datos válidos (no vacíos ni con ceros)."""
    validos = []
    no_validos = []
    for col in datos.columns:
        if not datos[col].isna().all() and (datos[col] != 0).any():
            validos.append(col)
        else:
            no_validos.append(col)
    return validos, no_validos

def calcular_porcentaje_vacios(datos):
    # Calcular el porcentaje de valores NaN por columna
    porcentaje_vacios = (datos.isna().sum() / len(datos)) * 100
    
    # Crear un DataFrame con los resultados
    df_nulos = pd.DataFrame({
        'Pluviómetro': porcentaje_vacios.index,
        'Porcentaje_Nulos': porcentaje_vacios.values
    })
    
    return df_nulos
    
def detectar_saltos_temporales(datos, intervalo=10):
    # Crear un DataFrame para almacenar los resultados
    saltos = pd.DataFrame(columns=['Pluviómetro', 'Inicio', 'Fin', 'Duración (min)'])
    
    # Iterar por cada columna (pluviómetro)
    for pluvio in datos.columns:
        # Detectar intervalos nulos consecutivos
        nulos = datos[pluvio].isna()
        
        # Calcular diferencias temporales
        cambios = nulos.astype(int).diff().fillna(0)
        
        # Detectar inicio y fin de intervalos nulos
        inicio_saltos = datos.index[cambios == 1]
        fin_saltos = datos.index[cambios == -1]
        
        # Si el intervalo empieza con nulos
        if nulos.iloc[0]:
            inicio_saltos = pd.Index([datos.index[0]]).append(inicio_saltos)
        
        # Si termina con nulos
        if nulos.iloc[-1]:
            fin_saltos = fin_saltos.append(pd.Index([datos.index[-1]]))
        
        # Calcular duración de los saltos
        duraciones = (fin_saltos - inicio_saltos).total_seconds() / 60  # minutos
        
        # Filtrar los saltos que cumplen con el intervalo mínimo
        saltos_detectados = duraciones[duraciones >= intervalo]
        
        # Guardar en el DataFrame
        for i in range(len(saltos_detectados)):
            saltos = pd.concat([saltos, pd.DataFrame({
                'Pluviómetro': [pluvio],
                'Inicio': [inicio_saltos[i]],
                'Fin': [fin_saltos[i]],
                'Duración (min)': [saltos_detectados.values[i]]  # Usar .values para obtener el valor
            })], ignore_index=True)
    
    return saltos

def acumulado(datos):
    # Crea un Dataframe con los acumulados por fecha y hora para cada pluviometro
    # Donde la diferencia es negativa, sumar el valor actual al acumulado anterior
    acumulados = datos.copy()

    for pluvio in datos.columns:
        acumulados[pluvio] = datos[pluvio].diff().apply(lambda x: x if x > 0 else 0).cumsum()
        
    return acumulados

def acumulado_total(acumulados):
    # Calcular el total acumulado para cada pluviometro a partir del dataframe acumulados (último valor de cada pluviómetro)
    acumulado_total = acumulados.iloc[-1].to_frame().T  # Última fila como DataFrame
    acumulado_total.index = ['Total']
    
    return acumulado_total

def instantaneo(datos):
    # Crea un Dataframe con los valores instantaneos por fecha y hora para cada pluviometro

    # Calcular el valor instantáneo (diferencias)
    datos = datos.diff()

    # Eliminar valores negativos (reinicios)
    datos = datos.map(lambda x: x if x > 0 else 0)
    return datos
    
def graficar_lluvia_instantanea(lluvia_instantanea):
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Graficar cada pluviómetro
    for columna in lluvia_instantanea.columns:
        plt.plot(lluvia_instantanea.index, lluvia_instantanea[columna], label=columna)

    # Etiquetas y título
    plt.xlabel('Evolución temporal (dd:mm:yy)')
    plt.ylabel('Precipitación instantáneas (en intervalos de 5 minutos)')
    plt.title('Grafico precipitaciones instantaneas')
    
     # Configurar el formato del eje X
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=[0, 30]))  # Etiquetas 00 y 30
    ax.xaxis.set_major_formatter(DateFormatter('%y/%m/%d %H:%M'))    # Formato Hora:Minuto
    
     # Alinear etiquetas desde el inicio (redondeo con numpy)
    inicio = np.datetime64(lluvia_instantanea.index.min(), 'h')  # Redondea al inicio de la hora
    fin = np.datetime64(lluvia_instantanea.index.max(), 'm') + np.timedelta64(30 - lluvia_instantanea.index.max().minute % 30, 'm')

    ax.set_xlim([inicio, fin])
    
    # Cuadriculado con líneas punteadas
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Rotar etiquetas verticalmente
    plt.xticks(rotation=90)
    
    # Mostrar leyenda
    plt.legend()
    plt.tight_layout()

    return fig

def graficar_lluvia_acumulado(lluvia_acumulada):
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Graficar cada pluviómetro
    for columna in lluvia_acumulada.columns:
        plt.plot(lluvia_acumulada.index, lluvia_acumulada[columna], label=columna)

    # Etiquetas y título
    plt.xlabel('Evolución temporal (dd:mm:yy)')
    plt.ylabel('Precipitación instantáneas (en intervalos de 5 minutos)')
    plt.title('Grafico acumulado precipitaciones')
    
     # Configurar el formato del eje X
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=[0, 30]))  # Etiquetas 00 y 30
    ax.xaxis.set_major_formatter(DateFormatter('%y/%m/%d %H:%M'))    # Formato Hora:Minuto
    
     # Alinear etiquetas desde el inicio (redondeo con numpy)
    inicio = np.datetime64(lluvia_acumulada.index.min(), 'h')  # Redondea al inicio de la hora
    fin = np.datetime64(lluvia_acumulada.index.max(), 'm') + np.timedelta64(30 - lluvia_acumulada.index.max().minute % 30, 'm')

    ax.set_xlim([inicio, fin])
    
    # Cuadriculado con líneas punteadas
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Rotar etiquetas verticalmente
    plt.xticks(rotation=90)
    
    # Mostrar leyenda
    plt.legend()
    plt.tight_layout()

    return fig
    