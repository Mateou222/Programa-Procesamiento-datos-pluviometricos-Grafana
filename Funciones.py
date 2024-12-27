from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter, HourLocator, MinuteLocator
import pandas as pd
import datetime as dt
import numpy as np
import os
from auxiliares import *
import matplotlib.dates as mdates


def leo_archivo():
    # TODO: Abro los archivos donde se encuentran las tablas con datos de grafana de pluviometros y depuro los datos
    
    contenido = os.listdir("Datos grafana")

    for archivo in contenido:
        if  archivo.endswith('.csv') and archivo.startswith("Precipitaciones"):
            with open("Datos grafana/" + archivo, encoding="utf-8") as archivopre:
                datos =  pd.read_csv(archivopre, encoding="utf-8")
   
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
    plt.figure(figsize=(12, 6))
    
    # Graficar cada pluviómetro
    for columna in lluvia_instantanea.columns:
        plt.plot(lluvia_instantanea.index, lluvia_instantanea[columna], label=columna)

    # Etiquetas y título
    plt.xlabel('Fecha y Hora')
    plt.ylabel('Precipitación instantáneas (en intervalos de 5 minutos)')
    plt.title('Evolución temporal (dd:mm:yy)')
    
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
    plt.show()

def calcular_porcentaje_nulos(datos):
    # Calcular el porcentaje de valores NaN por columna
    porcentaje_nulos = (datos.isna().sum() / len(datos)) * 100
    
    # Crear un DataFrame con los resultados
    df_nulos = pd.DataFrame({
        'Pluviómetro': porcentaje_nulos.index,
        'Porcentaje_Nulos': porcentaje_nulos.values
    })
    
    return df_nulos
    
datos = leo_archivo()

acumulados = acumulado(datos)

instantaneos = instantaneo(datos)

graficar_lluvia_instantanea(instantaneos)

print(calcular_porcentaje_nulos(datos))

"""
inicio = '2024-12-01 13:00:00'
fin = '2024-12-01 13:30:00'

intervalo = instantaneos.loc[inicio:fin]
print(intervalo)
"""