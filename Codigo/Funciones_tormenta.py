from Funciones_basicas import *

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

def limitar_df_temporal(df, limite_inf, limite_sup):
    # Filtrar el DataFrame dentro del rango de tiempo especificado
    return df[(df.index >= limite_inf) & (df.index <= limite_sup)]

def calcular_porcentaje_vacios(df_datos, df_config):
    # Calcular el porcentaje de valores NaN por columna
    porcentaje_vacios = (df_datos.isna().sum() / len(df_datos)) * 100
    
    lugares_nulos = [traducir_id_a_lugar(df_config, id_pluvio) for id_pluvio in porcentaje_vacios.index]
    
    # Crear un DataFrame con los resultados
    df_nulos = pd.DataFrame({
        'Pluviómetro': lugares_nulos,
        'Porcentaje_Nulos': porcentaje_vacios.values
    })
    
    return df_nulos

def detectar_saltos_temporales(df_datos, df_config, intervalo=5):
    # Crear un DataFrame para almacenar los resultados
    df_saltos_maximos = pd.DataFrame(columns=['Pluviómetro', 'Cantidad de saltos', 'Duración total (min)', 'Duración máx (min)', 'Inicio máx', 'Fin máx'])
    
    df_saltos = pd.DataFrame(columns=['Pluviómetro', 'Duración (min)', 'Inicio', 'Fin'])
    
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
        
        # Guardar todos los saltos detectados en df_saltos
        for i, duracion in saltos_detectados.items():
            df_saltos = pd.concat([df_saltos, pd.DataFrame({
                'Pluviómetro': [traducir_id_a_lugar(df_config, pluvio)],
                'Duración (min)': [duracion],
                'Inicio': [inicio_saltos[i]],
                'Fin': [fin_saltos[i]]
            })], ignore_index=True)
        
        # Acumular la duración de todos los saltos
        duracion_total = saltos_detectados.sum()  # Sumar las duraciones correctamente
        
        # Encontrar el salto más largo
        duracion_max = saltos_detectados.max()
        max_index = saltos_detectados.idxmax()
        
        # Guardar en el DataFrame
        df_saltos_maximos = pd.concat([df_saltos_maximos, pd.DataFrame({
            'Pluviómetro': [traducir_id_a_lugar(df_config, pluvio)],
            'Cantidad de saltos': [len(saltos_detectados)],
            'Duración total (min)': [duracion_total],
            'Duración máx (min)': [duracion_max],
            'Inicio máx': [inicio_saltos[max_index]],
            'Fin máx': [fin_saltos[max_index]],
        })], ignore_index=True)
    
    return df_saltos_maximos, df_saltos

def graficar_lluvia_con_saltos_tormenta(df_lluvia_instantanea, df_saltos, df_saltos_maximos, pluvio_seleccionado, df_config, ver_todos):
    
    if ver_todos:
        # Graficar lluvia instantánea primero
        fig = graficar_lluvia_instantanea_tormenta(df_lluvia_instantanea)
    else:
        pluvio_seleccionado_ID = traducir_lugar_a_id(df_config, pluvio_seleccionado)
        fig = graficar_lluvia_instantanea_tormenta(df_lluvia_instantanea[[pluvio_seleccionado_ID]])
    
    ax = fig.gca()  # Obtener el eje actual
    
    # Filtrar los saltos para el pluviómetro seleccionado
    saltos_pluvio = df_saltos[df_saltos['Pluviómetro'] == pluvio_seleccionado]
    salto_max_pluvio = df_saltos_maximos[df_saltos_maximos['Pluviómetro'] == pluvio_seleccionado]
    
    # Graficar todas las franjas de saltos
    if not saltos_pluvio.empty:
        for _, row in saltos_pluvio.iterrows():
            ax.axvspan(row['Inicio'], row['Fin'], color='red', alpha=0.3, label='Saltos')
    
    # Graficar el salto más grande en otro color
    if not salto_max_pluvio.empty:
        ax.axvspan(
            salto_max_pluvio['Inicio máx'].values[0],
            salto_max_pluvio['Fin máx'].values[0],
            color='blue',
            alpha=0.3,
            label='Salto más grande'
        )
    
    # Evitar etiquetas duplicadas en la leyenda
    handles, labels = ax.get_legend_handles_labels()
    unique_labels = dict(zip(labels, handles))
    ax.legend(unique_labels.values(), unique_labels.keys(), loc="upper left")
    
    return fig

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
  
def graficar_lluvia_instantanea_tormenta(df_lluvia_instantanea, intervalo_minutos=30):   
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
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=intervalo_minutos))  # Intervalo de etiqueta
    ax.xaxis.set_major_formatter(DateFormatter('%y/%m/%d %H:%M'))    # Formato Hora:Minuto
    
     # Alinear etiquetas desde el inicio (redondeo con numpy)
    inicio = np.datetime64(df_lluvia_instantanea.index.min(), 'h')  # Redondea al inicio de la hora
    fin = np.datetime64(df_lluvia_instantanea.index.max(), 'm') + np.timedelta64(30 - df_lluvia_instantanea.index.max().minute % intervalo_minutos, 'm')

    ax.set_xlim([inicio, fin])
    
    # Cuadriculado con líneas punteadas
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Rotar etiquetas verticalmente
    plt.xticks(rotation=90)
    
    # Mostrar leyenda
    plt.legend(loc= "upper left")
    plt.tight_layout()

    return fig

def graficar_lluvia_acumulado_tormenta(df_lluvia_acumulada):
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

    # Identificar el nombre del pluviómetro y su máximo
    pluvio_maximo = max(maximos_por_pluvio, key=maximos_por_pluvio.get)
    max_valor = maximos_por_pluvio[pluvio_maximo]
    
    return max_valor, pluvio_maximo

def calcular_precipitacion_para_tr(df):
    precipitaciones = []

    for ventana in duracion_tormenta:
        # Calcular el máximo usando la función de suma de ventana
        max_valor, pluvio_maximo = max_suma_ventana_df(df, ventana)
               
        # Guardar el valor en la lista
        precipitaciones.append((ventana, max_valor, pluvio_maximo))

    return precipitaciones

def calcular_precipitacion_pluvio(df, pluvio):
    # Filtrar solo la columna del pluviómetro seleccionado
    df_pluvio = df[[pluvio]]  # Mantener formato DataFrame con doble corchete
    
    # Reutilizar la función de cálculo
    return calcular_precipitacion_para_tr(df_pluvio)

def grafica_tr(lista_tr, precipitaciones, limite_precipitacion, limite_tiempo, etiqueta, titulo):
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
