from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter
import pandas as pd
import numpy as np
import matplotlib.dates as mdates


# Variable global
duracion_tormenta = [10, 20, 30, 60, 120, 180, 360, 720, 1440]

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

def leer_archivo_verificador(archivo, df_datos):
    # Aquí procesamos el archivo seleccionado
    df_datos_validador = pd.read_csv(archivo, encoding="latin-1", sep=';', decimal=',')
    
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
    
    df_seleccionado = df_datos_validador[['fecha', 'precipitacia3n_-_valor_crudo']]
    
    # Agrupar por tiempo redondeado y consolidar valores
    df_seleccionado = df_seleccionado.groupby('fecha').max()  # max() mantiene el valor no nulo más alto por grupo
        
    # Cambiar el formato de la columna de fecha
    df_seleccionado.index = df_seleccionado.index.strftime('%Y-%d-%m %H:%M:%S')
    
     # Si hay valores faltantes, rellena hacia adelante
    df_seleccionado = df_seleccionado.bfill()
    
    df_datos.index = pd.to_datetime(df_datos.index)
    
    # Asegurarse de que los índices son de tipo datetime en ambos DataFrames
    df_seleccionado.index = pd.to_datetime(df_seleccionado.index)
    
    # Filtrar df_seleccionado para que coincida con el rango de fechas de df_datos
    start_date = df_datos.index.min()
    end_date = df_datos.index.max()
    
    df_seleccionado = df_seleccionado[(df_seleccionado.index >= start_date) & (df_seleccionado.index <= end_date)]
    
    # Reindexado y alineación flexible por fecha más cercana
    df_seleccionado = df_seleccionado.reindex(df_datos.index, method='ffill')  # 'ffill' para llenar con el valor más cercano hacia adelante
    
   # Agregar columna con nombre de la estación
    nombre_columna = df_datos_validador['estacia3n'].iloc[0]  # Obtener nombre de la estación
    df_datos[nombre_columna] = df_seleccionado['precipitacia3n_-_valor_crudo']
    
    return df_datos


def limitar_df_temporal(df, limite_inf, limite_sup):
    # Filtrar el DataFrame dentro del rango de tiempo especificado
    return df[(df.index >= limite_inf) & (df.index <= limite_sup)]

def calcular_porcentaje_vacios(df_datos):
    # Calcular el porcentaje de valores NaN por columna
    porcentaje_vacios = (df_datos.isna().sum() / len(df_datos)) * 100
    
    # Crear un DataFrame con los resultados
    df_nulos = pd.DataFrame({
        'Pluviómetro': porcentaje_vacios.index,
        'Porcentaje_Nulos': porcentaje_vacios.values
    })
    
    return df_nulos

def detectar_saltos_temporales(df_datos, intervalo=10):
    # Crear un DataFrame para almacenar los resultados
    df_saltos = pd.DataFrame(columns=['Pluviómetro', 'Cantidad de saltos', 'Duración total (min)', 'Duración máx (min)', 'Inicio máx', 'Fin máx'])
    
    # Iterar por cada columna (pluviómetro)
    for pluvio in df_datos.columns:
        # Detectar intervalos nulos consecutivos
        nulos = df_datos[pluvio].isna()
        
        # Calcular diferencias temporales
        cambios = nulos.astype(int).diff().fillna(0)
        
        # Detectar inicio y fin de intervalos nulos
        inicio_saltos = df_datos.index[cambios == 1]
        fin_saltos = df_datos.index[cambios == -1]
        
        # Si el intervalo empieza con nulos
        if nulos.iloc[0]:
            inicio_saltos = pd.Index([df_datos.index[0]]).append(inicio_saltos)
        
        # Si termina con nulos
        if nulos.iloc[-1]:
            fin_saltos = fin_saltos.append(pd.Index([df_datos.index[-1]]))
        
        # Calcular duración de los saltos
        duraciones = (fin_saltos - inicio_saltos).total_seconds() / 60  # minutos
        
        # Filtrar los saltos que cumplen con el intervalo mínimo y convertir a Series numérica
        saltos_detectados = pd.Series(duraciones[duraciones >= intervalo])
        
        # Si no hay saltos, continuar con el siguiente pluviómetro
        if saltos_detectados.empty:
            continue
        
        # Acumular la duración de todos los saltos
        duracion_total = saltos_detectados.sum()  # Sumar las duraciones correctamente
        
        # Encontrar el salto más largo
        duracion_max = saltos_detectados.max()
        max_index = saltos_detectados.idxmax()
        
        # Guardar en el DataFrame
        df_saltos = pd.concat([df_saltos, pd.DataFrame({
            'Pluviómetro': [pluvio],
            'Cantidad de saltos': [len(saltos_detectados)],
            'Duración total (min)': [duracion_total],
            'Duración máx (min)': [duracion_max],
            'Inicio máx': [inicio_saltos[max_index]],
            'Fin máx': [fin_saltos[max_index]],
        })], ignore_index=True)
    
    return df_saltos

def acumulados(df_datos):
    # Crea un Dataframe con los acumulados por fecha y hora para cada pluviometro
    # Donde la diferencia es negativa, sumar el valor actual al acumulado anterior
    df_acumulados = df_datos.copy()

    for pluvio in df_datos.columns:
        df_acumulados[pluvio] = df_datos[pluvio].diff().apply(lambda x: x if x > 0 else 0).cumsum()
        
    return df_acumulados

def acumulado_total(acumulados):
    # Calcular el total acumulado para cada pluviometro a partir del dataframe acumulados (último valor de cada pluviómetro)
    acumulado_total = acumulados.iloc[-1].to_frame().T  # Última fila como DataFrame
    acumulado_total.index = ['Total']
    
    return acumulado_total

def obtener_pluviometros_validos(df_datos):
    """Devuelve los nombres de los pluviómetros con datos válidos (no vacíos ni con ceros) y elimina aquellos cuyo acumulado total es 0."""
    validos = []
    no_validos = []
    
    # Llamamos a la función para obtener los acumulados
    df_acumulados = acumulados(df_datos)
    acumulado_total_df = acumulado_total(df_acumulados)
    for col in df_datos.columns:
        # Comprobar si el acumulado total de un pluviómetro es 0
        if acumulado_total_df[col].iloc[0] == 0:
            no_validos.append(col)
        # Comprobar si la columna tiene datos válidos (sin NaN ni 0)
        elif not df_datos[col].isna().all() and (df_datos[col] != 0).any():
            validos.append(col)
        else:
            no_validos.append(col)
    
    return validos, no_validos

def calcular_instantaneos(df_datos):
    # Crea un Dataframe con los valores instantaneos por fecha y hora para cada pluviometro

    # Calcular el valor instantáneo (diferencias)
    df_datos = df_datos.diff()

    # Eliminar valores negativos (reinicios)
    df_datos = df_datos.map(lambda x: x if x > 0 else 0)
    return df_datos
    
def graficar_lluvia_instantanea(df_lluvia_instantanea):   
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Graficar cada pluviómetro
    for columna in df_lluvia_instantanea.columns:
        plt.plot(df_lluvia_instantanea.index, df_lluvia_instantanea[columna], label=columna)

    # Etiquetas y título
    plt.xlabel('Evolución temporal (dd:mm:yy)')
    plt.ylabel('Precipitación instantáneas (en intervalos de 5 minutos)')
    plt.title('Grafico precipitaciones instantaneas')
    
     # Configurar el formato del eje X
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=[0, 30]))  # Etiquetas 00 y 30
    ax.xaxis.set_major_formatter(DateFormatter('%y/%m/%d %H:%M'))    # Formato Hora:Minuto
    
     # Alinear etiquetas desde el inicio (redondeo con numpy)
    inicio = np.datetime64(df_lluvia_instantanea.index.min(), 'h')  # Redondea al inicio de la hora
    fin = np.datetime64(df_lluvia_instantanea.index.max(), 'm') + np.timedelta64(30 - df_lluvia_instantanea.index.max().minute % 30, 'm')

    ax.set_xlim([inicio, fin])
    
    # Cuadriculado con líneas punteadas
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Rotar etiquetas verticalmente
    plt.xticks(rotation=90)
    
    # Mostrar leyenda
    plt.legend(loc= "upper left")
    plt.tight_layout()

    return fig

def graficar_lluvia_acumulado(df_lluvia_acumulada):
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Graficar cada pluviómetro
    for columna in df_lluvia_acumulada.columns:
        plt.plot(df_lluvia_acumulada.index, df_lluvia_acumulada[columna], label=columna)

    # Etiquetas y título
    plt.xlabel('Evolución temporal (dd:mm:yy)')
    plt.ylabel('Precipitación instantáneas (en intervalos de 5 minutos)')
    plt.title('Grafico acumulado precipitaciones')
    
     # Configurar el formato del eje X
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=[0, 30]))  # Etiquetas 00 y 30
    ax.xaxis.set_major_formatter(DateFormatter('%y/%m/%d %H:%M'))    # Formato Hora:Minuto
    
     # Alinear etiquetas desde el inicio (redondeo con numpy)
    inicio = np.datetime64(df_lluvia_acumulada.index.min(), 'h')  # Redondea al inicio de la hora
    fin = np.datetime64(df_lluvia_acumulada.index.max(), 'm') + np.timedelta64(30 - df_lluvia_acumulada.index.max().minute % 30, 'm')

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

"""

verificador = leer_archivo_verificador("C:/Users/Dica/Documents/Tormentas/Datos grafana/Datos_Calidad_de_Aire.csv", leer_archivo_principal("C:/Users/Dica/Documents/Tormentas/Datos grafana/Precipitaciones - Acumulado diario-data-as-joinbyfield-2024-12-30 11_19_57.csv"))

fig = graficar_lluvia_instantanea(calcular_instantaneos(verificador))
fig.show()

"""