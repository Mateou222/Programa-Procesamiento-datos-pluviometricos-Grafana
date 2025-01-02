from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter
import pandas as pd
import numpy as np
import matplotlib.dates as mdates

# Variable global
duracion_tormenta = [10, 20, 30, 60, 120, 180, 360, 720, 1440]

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

def obtener_pluviometros_validos(datos):
    """Devuelve los nombres de los pluviómetros con datos válidos (no vacíos ni con ceros) y elimina aquellos cuyo acumulado total es 0."""
    validos = []
    no_validos = []
    
    # Llamamos a la función para obtener los acumulados
    acumulados = acumulado(datos)
    acumulado_total_df = acumulado_total(acumulados)
    for col in datos.columns:
        # Comprobar si el acumulado total de un pluviómetro es 0
        if acumulado_total_df[col].iloc[0] == 0:
            no_validos.append(col)
        # Comprobar si la columna tiene datos válidos (sin NaN ni 0)
        elif not datos[col].isna().all() and (datos[col] != 0).any():
            validos.append(col)
        else:
            no_validos.append(col)
    
    return validos, no_validos

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
    plt.legend(loc= "upper left")
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
    plt.legend(loc= "upper left")
    plt.tight_layout()

    return fig

def max_suma_ventana_df(df, ventana):
    # Convertir la ventana a intervalos (cada 5 minutos)
    intervalos = ventana // 5
    
    # Diccionario para almacenar el máximo por pluviómetro
    maximos_por_pluvio = {}

    # Calcular el máximo para cada pluviómetro (columna)
    for columna in df.columns:
        precipitaciones = df[columna].dropna().tolist()
        sumas_ventana = [sum(precipitaciones[i:i + intervalos]) 
                         for i in range(len(precipitaciones) - intervalos + 1)]
        
        # Guardar el máximo en el diccionario
        maximos_por_pluvio[columna] = max(sumas_ventana) if sumas_ventana else 0

    # Convertir el resultado a Serie de pandas
    return pd.Series(maximos_por_pluvio, name=f"Máximo en ventana {ventana} min")

def calcular_precipitacion_para_tr(df):
    precipitaciones = []

    for ventana in duracion_tormenta:
        # Calcular el máximo usando la función de suma de ventana
        resultado = max_suma_ventana_df(df, ventana)
        
        # Obtener el valor máximo
        maximo_valor = resultado.max()
        
        # Guardar el valor en la lista
        precipitaciones.append(maximo_valor)

    return precipitaciones

def calcular_precipitacion_pluvio(df, pluvio):
    # Filtrar solo la columna del pluviómetro seleccionado
    df_pluvio = df[[pluvio]]  # Mantener formato DataFrame con doble corchete
    
    # Reutilizar la función de cálculo
    return calcular_precipitacion_para_tr(df_pluvio)

def grafica_tr(lista_tr, precipitaciones, limite_precipitacion, limite_tiempo, etiqueta, titulo):
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

    # Crear la figura
    fig, ax = plt.subplots(figsize=(8, 4))

    # Graficar solo los TR que estén activados en la lista_tr
    tr_names = list(precipitacion_tr.keys())
    
    for i, tr in enumerate(tr_names):
        if lista_tr[i] == 1:  # Si el valor en lista_tr es 1, graficar ese TR
            ax.plot(duracion_tormenta, precipitacion_tr[tr], label=tr, linestyle='-', linewidth=1.5)
    
    # Graficar los puntos de la precipitacion
    if precipitaciones is not None:
        ax.scatter(duracion_tormenta, precipitaciones, label=etiqueta, color='red', marker='o', facecolors="none", linewidth=1.5)
        
    # Etiquetas y límites
    ax.set_title(titulo, fontsize=12)
    ax.set_xlabel('Minutos de Duración de la Tormenta', fontsize=10)
    ax.set_ylabel('Precipitación (mm)', fontsize=10)
    ax.legend(loc="upper left")
    ax.set_ylim(0, limite_precipitacion)
    ax.set_xlim(0, limite_tiempo)
    ax.grid(True)
    
    # Retornar la figura
    return fig

