from Funciones_basicas import *
from Funciones_config import *
from Funciones_mensual import *

def obtener_ubicaciones(df_config):
    return {row['ID']: (row['X'], row['Y']) for _, row in df_config.iterrows()}

def obtener_precipitaciones(df_lluvias, nombres_equipos):
    """
    Extrae los valores de precipitación de los nombres de estaciones en el DataFrame.
    
    Parámetros:
    - df_lluvias: DataFrame con las precipitaciones acumuladas.
    - nombres_equipos: Lista con los nombres de los equipos a extraer.

    Retorna:
    - np.array con los valores de precipitación en el mismo orden que nombres_equipos.
    """
    return np.array([df_lluvias.at["Total", nombre] if nombre in df_lluvias.columns else 0 for nombre in nombres_equipos])

def extraer_coordenadas(ubicaciones, df_acumulados_diarios_total):
    nombres = list(ubicaciones.keys())
    X = np.array([ubicaciones[n][0] for n in nombres])
    Y = np.array([ubicaciones[n][1] for n in nombres])
    Z = obtener_precipitaciones(df_acumulados_diarios_total, nombres)
    return nombres, X, Y, Z

def interpolar_idw(X, Y, Z, xq, yq, power=2):
    Xq, Yq = np.meshgrid(xq, yq)
    Zq = np.zeros(Xq.shape)
    for i in range(Xq.shape[0]):
        for j in range(Xq.shape[1]):
            distances = np.sqrt((X - Xq[i, j])**2 + (Y - Yq[i, j])**2)
            weights = 1 / distances**power
            weights[distances == 0] = np.inf
            Zq[i, j] = np.sum(weights * Z) / np.sum(weights)
    return Xq, Yq, Zq

def determinar_niveles(Zq, num_niveles=6):
    minZ, maxZ = np.min(Zq), np.max(Zq)
    rango = maxZ - minZ
    multiplo = np.ceil(rango / num_niveles)
    niveles = np.arange(np.floor(minZ / multiplo) * multiplo, np.ceil(maxZ / multiplo) * multiplo + multiplo, multiplo)
    if len(niveles) < 6:
        raise ValueError('No hay suficientes niveles para crear el mapa de isoyetas.')
    return niveles

def obtener_posicion_adecuada(x, y, i, X, Y):
    offset_x, offset_y = 150, 150
    for j in range(len(X)):
        if i != j:
            if np.sqrt((x - X[j])**2 + (y - Y[j])**2) < 100:
                offset_x, offset_y = 50, 50
                break
    return x + offset_x, y + offset_y

def fig_graficar_isoyetas(X, Y, Zq, Xq, Yq, niveles, nombres, mapa_fondo_path):
    fig, ax = plt.subplots(figsize=(8, 6))  # Crear la figura y los ejes
    cs = ax.contourf(Xq, Yq, Zq, levels=niveles, cmap="Blues", alpha=0.8)  # Usar los niveles predefinidos
    
    # Cargar el mapa de fondo
    mapa_fondo = mpimg.imread(mapa_fondo_path)
    extent = [551332.763, 590932.763, 6131816.936, 6160416.936]
    ax.imshow(mapa_fondo, extent=extent, origin='upper')
    
    # Agregar las ubicaciones y nombres de las estaciones
    ax.scatter(X, Y, c='red', edgecolors='black', zorder=5)
    for i, nombre in enumerate(nombres):
        x_pos, y_pos = obtener_posicion_adecuada(X[i], Y[i], i, X, Y)
        ax.text(x_pos, y_pos, nombre, fontsize=8, color='blue',
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=0.2))
    
    # Graficar las curvas de nivel con sus etiquetas
    contour_lines = ax.contour(Xq, Yq, Zq, levels=niveles, colors='black')  # Añadir las curvas de nivel
    ax.clabel(contour_lines, inline=True, fontsize=8, fmt='%1.1f', colors='black')  # Etiquetas para las curvas de nivel
    
    ax.set_title('Mapa de Isoyetas usando IDW')
    ax.set_aspect('equal')
    
    # Retornar la figura
    return fig

def graficar_isoyetas(df_config, df_acumulados_diarios_total):
    ubicaciones = obtener_ubicaciones(df_config)
    nombres, X, Y, Z = extraer_coordenadas(ubicaciones, df_acumulados_diarios_total)
    xq = np.linspace(551332.763, 590932.763, 300)
    yq = np.linspace(6131816.936, 6160416.936, 300)
    Xq, Yq, Zq = interpolar_idw(X, Y, Z, xq, yq)
    niveles = determinar_niveles(Zq)
    return fig_graficar_isoyetas(X, Y, Zq, Xq, Yq, niveles, nombres, 'MONTEVIDEO.png')

def graficar_isoyetas_tr(df_config, df_acumulados_diarios_total, tr):
    ubicaciones = obtener_ubicaciones(df_config)
    nombres, X, Y, Z = extraer_coordenadas(ubicaciones, df_acumulados_diarios_total)
    xq = np.linspace(551332.763, 590932.763, 300)
    yq = np.linspace(6131816.936, 6160416.936, 300)
    Xq, Yq, Zq = interpolar_idw(X, Y, Z, xq, yq)
    
    # Definir los niveles preestablecidos
    #tr = [15.1, 19.4, 22.2, 24.9, 25.8, 28.5, 31.1] 
    return fig_graficar_isoyetas(X, Y, Zq, Xq, Yq, tr, nombres, 'MONTEVIDEO.png')

"""

df_datos = leer_archivo_principal("C:\\Users\\Usuario\\Documents\\Programa-Procesamiento-datos-pluviometricos-Grafana\\Datos grafana\\mensual.csv")

df_config = cargar_config()
df_config = agregar_equipos_nuevos_config(df_config, df_datos)

df_config = eliminar_lugares_no_existentes_config(df_config, df_datos)


df_instantaneo = calcular_instantaneos(df_datos)
df_acumulados_diarios = calcular_acumulados_diarios(df_instantaneo)
df_acumulados_diarios = traducir_columnas_lugar_a_id(df_config, df_acumulados_diarios)
df_acumulados_diarios_total = acumulado_diarios_total(df_acumulados_diarios).tail(1)



main(df_config, df_acumulados_diarios_total)
"""