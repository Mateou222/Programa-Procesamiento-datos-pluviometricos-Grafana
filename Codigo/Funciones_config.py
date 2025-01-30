from Funciones_basicas import *


# Crear o cargar el dataframe con las configuraciones
def cargar_config():
    if os.path.exists('Lugares-ID.csv'):
        df_config = pd.read_csv('Lugares-ID.csv', encoding="utf-8")
    else:
        # Si no existe el archivo, crear un dataframe vacío con las columnas esperadas
        df_config = pd.DataFrame(columns=['Lugar', 'ID'])
    df_config["Lugar"] = df_config["Lugar"].apply(eliminar_tildes)
    
    if os.path.exists('Coordenadas_Equipos.csv'):
        df_coord = pd.read_csv('Coordenadas_Equipos.csv', encoding="utf-8")
    else:
        # Si no existe el archivo, crear un dataframe vacío con las columnas esperadas
        df_coord = pd.DataFrame(columns=['Lugar', 'X', 'Y'])
    
    # Combinar ambos DataFrames por la columna 'Lugar', manteniendo todos los valores
    df_config = pd.merge(df_config, df_coord, on='Lugar', how='outer')
      
    return df_config

# Guardar el dataframe
def guardar_config(df_config):
    if os.path.exists('Coordenadas_Equipos.csv'):
        df_coord_archivo = pd.read_csv('Coordenadas_Equipos.csv', encoding="utf-8")
    else:
        df_coord_archivo = pd.DataFrame(columns=["Lugar", "X", "Y"])
        
    df_coord = df_config[["Lugar", "X", "Y"]]
    
    df_coord_actualizado = pd.merge(df_coord_archivo, df_coord, on="Lugar", how="outer", suffixes=('_old', ''))
    for col in ["X", "Y"]:
        df_coord_actualizado[col] = df_coord_actualizado[f"{col}"].combine_first(df_coord_actualizado[f"{col}_old"])
        
    # Eliminar columnas temporales
    df_coord_actualizado = df_coord_actualizado[["Lugar", "X", "Y"]]
    
    df_coord_actualizado = df_coord_actualizado.dropna(subset=["X", "Y"])
    
    # Guardar el DataFrame actualizado en el archivo
    df_coord_actualizado.to_csv('Coordenadas_Equipos.csv', index=False, encoding='utf-8')
        
    df_ID = df_config[["Lugar", "ID"]]
    df_ID.to_csv('Lugares-ID.csv', index=False, encoding='utf-8')

# Función para agregar nuevos lugares y columnas a la configuración
def agregar_equipos_nuevos_config(df_config, df_datos):
    # Eliminar tildes en los nombres de las columnas de df_datos
    df_datos.columns = [eliminar_tildes(col) for col in df_datos.columns]
    
    # Agregar nuevos lugares que no estén en df_config (solo en las filas)
    for col in df_datos.columns:
        # Verificar si el "lugar" (nombre de la columna) ya existe en df_config como fila
        if col not in df_config['Lugar'].values:
            # Crear una nueva fila con el "lugar" y un ID vacío o el valor correspondiente
            new_row = pd.DataFrame({'Lugar': [col], 'ID': [None], 'X': [None], 'Y': [None]})
            
            # Asegurarse de que no haya columnas vacías antes de la concatenación
            new_row = new_row.dropna(axis=1, how='all')  # Eliminar columnas vacías
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

def detectar_Coord_X_faltante_config(df_config):
    lugares_faltantes_X = df_config[df_config['X'].isna()]['Lugar'].tolist()
    return lugares_faltantes_X

def detectar_Coord_Y_faltante_config(df_config):
    lugares_faltantes_Y = df_config[df_config['Y'].isna()]['Lugar'].tolist()
    return lugares_faltantes_Y

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

# Función para convertir coordenadas
def convertir_a_UTM(df_coord):
    # Crear listas para almacenar las nuevas coordenadas
    coordenadas_UTM_X = []
    coordenadas_UTM_Y = []
    
    # Iterar sobre las filas del DataFrame
    for _, row in df_coord.iterrows():
        lat = row['latitud']
        lon = row['longitud']
        
        # Convertir de Latitud/Longitud (EPSG:4326) a UTM (EPSG:32721)
        x, y = transformer.transform(lon, lat)  # Cambié el orden para lon, lat
        
        # Almacenar los resultados
        coordenadas_UTM_X.append(x)
        coordenadas_UTM_Y.append(y)
    
    df_coord = df_coord.drop('latitud', axis=1)
    df_coord = df_coord.drop('longitud', axis=1)
    # Agregar las nuevas columnas al DataFrame
    df_coord['X'] = coordenadas_UTM_X
    df_coord['Y'] = coordenadas_UTM_Y
    
    return df_coord

def leer_archivo_coordenadas_traduccion(archivo):
    # Abro los archivos donde se encuentran las tablas con datos de grafana de pluviometros y depuro los datos
    
    # Aquí procesamos el archivo seleccionado
    df_coord = pd.read_csv(archivo, encoding="utf-8")
    df_coord.columns = [eliminar_tildes(col) for col in df_coord.columns]
    df_coord.index = [eliminar_tildes(row) for row in df_coord["Descripcion"]]
    df_coord = df_coord[["longitud", "latitud"]]
    
    df_coord.index = df_coord.index.str.replace('Pluviometro - ', '').str.replace('Estacion Meteorologica - ', '')
    
    df_convertido = convertir_a_UTM(df_coord)
    
    df_convertido = df_convertido.reset_index()

    # Renombrar la columna del índice si es necesario
    df_convertido.rename(columns={'index': 'Lugar'}, inplace=True)
    
    return df_convertido

#leer_archivo_coordenadas_traduccion("C:\\Users\\Usuario\\Documents\\Programa-Procesamiento-datos-pluviometricos-Grafana\\Datos grafana\\Ubicación de sensores de precipitación-data-2025-01-28 12_29_19.csv")

"""

leer_archivo_coordenadas_traduccion("C:\\Users\\Usuario\\Documents\\Programa-Procesamiento-datos-pluviometricos-Grafana\\Datos grafana\\Ubicación de sensores de precipitación-data-2025-01-28 12_29_19.csv")
df_config = cargar_config()
df_datos = leer_archivo_principal("C:\\Users\\Usuario\\Documents\\Programa-Procesamiento-datos-pluviometricos-Grafana\\Datos grafana\\mensual.csv")
df_config = agregar_equipos_nuevos_config(df_config, df_datos)

df_config = eliminar_lugares_no_existentes_config(df_config, df_datos)

guardar_config(df_config)

"""