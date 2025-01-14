
import locale
import pandas as pd

from Funciones_basicas import *
from Funciones_tormenta import *

# Establecer la localización en español
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

lluvia_historico = {
    1: [38.75, 71.50, 120.00, 448.00],
    2: [45.50, 80.50, 120.55, 276.00],
    3: [47.00, 84.40, 133.95, 450.30],
    4: [42.75, 74.20, 141.50, 499.00],
    5: [39.43, 78.00, 140.75, 320,00],
    6: [43.75, 80.60, 127.00, 347.00],
    7: [45.00, 65.00, 105.73, 243.00],
    8: [38.25, 72.00, 113.25, 360.00],
    9: [47.75, 77.00, 128.25, 295.00],
    10: [46.45, 71.00, 120.98, 265.00],
    11: [43.53, 76.25, 118.50, 251.00],
    12: [47.50, 64.50, 105.15, 286.00]
}

def valor_lluvias_historicas(mes):
    # Comprobar si el mes es válido
    if mes in lluvia_historico:
        return lluvia_historico[mes]  # Devolver los valores de la columna como lista
    else:
        return f"Mes {mes} no válido"

def obtener_mes(df_acumulados_diarios):
    # Convertir el índice a tipo datetime si no lo es
    if not pd.api.types.is_datetime64_any_dtype(df_acumulados_diarios.index):
        df_acumulados_diarios.index = pd.to_datetime(df_acumulados_diarios.index, errors='coerce')

    # Obtener el valor central (aproximado)
    valor_central = df_acumulados_diarios.index[len(df_acumulados_diarios) // 2]

    # Extraer el mes como entero
    mes = valor_central.month

    return mes

def numero_a_mes(numero_mes):
    # Obtener el nombre del mes en español
    meses_es = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    if 1 <= numero_mes <= 12:
        return meses_es[numero_mes - 1]
    else:
        raise ValueError("El número debe estar entre 1 y 12.")

def graficar_acumulados_barras(df_acumulados_diarios):
    #df_acumulado_total = acumulado_total(acumulados(df_datos))
    
    mes = obtener_mes(df_acumulados_diarios)
    
    df_acumulado_total = df_acumulados_diarios.sum()
    mes_lluvia_historica = valor_lluvias_historicas(mes)
    
    # Crear la figura y el eje
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Graficar cada pluviómetro
    ax.bar(df_acumulado_total.index, df_acumulado_total.values, color='blue', label="Pluviómetros", alpha=0.8)     
    # Etiquetas y título
    ax.set_xlabel('Pluviómetro')
    
    ax.set_ylabel('Acumulado total (mm)')
    ax.set_title('Acumulado Total de Precipitación por Pluviómetro')
    
    # Rotar etiquetas del eje X para mejor visibilidad
    plt.xticks(rotation=45, ha='right')
    
    # Cuadriculado con líneas punteadas
    plt.grid(True, axis='both', linestyle='--', linewidth=0.5)
    
    # Colores diferentes para cada percentil
    colores_percentiles = ['red', 'green', 'orange', 'purple']
    labels_percentiles = ["Primer cuartil", "Mediana", "Tercer cuartil", "Maximo"]  # Lista para los labels de la leyenda
    for i, valor in enumerate(mes_lluvia_historica):
        # Dibujar la línea horizontal para cada percentil
        ax.axhline(y=valor, color=colores_percentiles[i], linestyle='--', linewidth=2, label=f'{labels_percentiles[i]}')
    
    # Añadir la leyenda
    ax.legend(title='', loc='upper left', bbox_to_anchor=(1, 1))
    
    # Ajustar el layout
    plt.tight_layout()

    # Pausar la ejecución del script hasta presionar Enter
    return fig

def calcular_acumulados_diarios(df_instantaneo):
    # Asegurarse de que el índice de 'df_datos' sea de tipo datetime (si no lo es ya)
    df_instantaneo.index = pd.to_datetime(df_instantaneo.index)
    
    # Agrupar los datos por día (sin hora) y sumar los valores de lluvia por día para cada pluviómetro
    df_acumulados_diarios = df_instantaneo.groupby(df_instantaneo.index.date).sum()
    
    # Devolver el DataFrame con las sumas de lluvia por día
    return df_acumulados_diarios

def graficar_acumulados_diarios(df_acumulados_diarios):
    #df_acumulados_diarios_suma = acumulados_diarios_suma(df_datos)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Graficar cada pluviómetro con los acumulados diarios
    for columna in df_acumulados_diarios.columns:
        plt.plot(df_acumulados_diarios.index, df_acumulados_diarios[columna], label=columna)

    # Etiquetas y título
    plt.xlabel('Día')
    plt.ylabel('Acumulado de precipitación (mm)')
    plt.title('Acumulado diario de precipitación por pluviómetro')
    
    # Configurar el formato del eje X para mostrar más días
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))  # Intervalo de 1 día
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))  # Formato: Mes abreviado y día
    
    # Ajustar límites del eje X según los días
    ax.set_xlim([df_acumulados_diarios.index.min(), df_acumulados_diarios.index.max()])
    
    # Cuadriculado con líneas punteadas
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Rotar etiquetas del eje X para mayor claridad
    plt.xticks(rotation=45, ha='right')
    
    # Añadir la leyenda
    ax.legend(title='', loc='upper left', bbox_to_anchor=(1, 1))
    
    # Ajustar el layout para que todo quede visible
    plt.tight_layout()
    
    return fig


def eliminar_filas_zeros_na(df):
    # Eliminar filas donde todos los valores sean NaN o 0
    df_cleaned = df[(df != 0).any(axis=1)]  # Filtra filas que no tienen todos los valores en 0
    df_cleaned = df_cleaned.dropna(how='all')  # Elimina filas que sean NaN en todas las columnas

    return df_cleaned

def calcular_correlacion(df):
    # Calcula la correlación entre las columnas del DataFrame
    df_correlacion = df.corr()

    # Poner ceros en la parte inferior izquierda de la matriz de correlación
    df_correlacion = df_correlacion.where(np.triu(np.ones(df_correlacion.shape), k=0).astype(bool))
    
    return df_correlacion

def tabla_correlacion(df_acumulados_diarios):
    # Eliminar filas donde todos los valores sean NaN o 0 
    df_acumulados_diarios = eliminar_filas_zeros_na(df_acumulados_diarios)
    
    df_correlacion = calcular_correlacion(df_acumulados_diarios)
    
    # Redondear los valores a dos dígitos decimales
    df_correlacion = df_correlacion.round(2)
    
    return df_correlacion

def grafica_lluvias_respecto_inumet(df_acumulados_diarios):
    # Eliminar filas donde todos los valores sean NaN o 0
    df_acumulados_diarios = eliminar_filas_zeros_na(df_acumulados_diarios)
    
    # Ordenar cada columna de menor a mayor
    df_acumulados_diarios = df_acumulados_diarios.apply(lambda col: col.sort_values().reset_index(drop=True))
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    for columna in df_acumulados_diarios.columns:
        if columna != 'INUMET':  # Asegurarse de graficar la columna 'INUMET' por otro lado
            plt.plot(df_acumulados_diarios['INUMET'], df_acumulados_diarios[columna], label=columna)
        else:
            plt.plot(df_acumulados_diarios['INUMET'], df_acumulados_diarios[columna], label=columna, linestyle="--", linewidth=2, color="red")
                    
    # Etiquetas y título
    plt.xlabel('INUMET (mm)')  # Eje X: valores de precipitación INUMET
    plt.ylabel('Precipitación (mm) por Pluviómetro')  # Eje Y: valores de precipitación para cada pluviómetro
    plt.title('Relación de precipitación por pluviómetro respecto a INUMET')
    
    # Cuadriculado con líneas punteadas
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Añadir la leyenda
    ax.legend(title='', loc='upper left', bbox_to_anchor=(1, 1))
    
    # Ajustar el layout para que todo quede visible
    plt.tight_layout()
        
    return fig
    

"""

df_datos = leer_archivo_principal("C:/Users/Dica/Documents/Tormentas/Datos grafana/mensual.csv")

df_datos = leer_archivo_verificador("C:/Users/Dica/Documents/Tormentas/Datos grafana/Datos_Calidad_de_Aire (3).csv", df_datos)

df_instantaneo = calcular_instantaneos(df_datos)

df_acumulados_diarios = acumulados_diarios_suma(df_instantaneo)

df_acumulados_diarios = leer_archivo_inumet("C:/Users/Dica/Documents/Tormentas/Datos grafana/INUMET.csv", df_acumulados_diarios)

#df_acumulados_diarios.to_csv('df_acumulados_diarios.csv', index=False)

df_acumulado = acumulados(df_datos)

graficar_acumulados_barras(df_acumulado)

"""



