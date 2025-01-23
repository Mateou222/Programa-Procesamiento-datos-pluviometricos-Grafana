import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist

# Datos de ejemplo (coordenadas UTM y valores de precipitación)
ubicaciones = [
    ("MI", 570969.263, 6140832.411),
    ("AL", 587675.4, 6140719.057),
    ("PCV", 575573, 6145098),
    ("AN", 574444, 6136895),
    ("CERRO", 568868.112, 6139085.139),
    ("CA", 572989, 6137438),
    ("COLON", 568927.216, 6146677.45),
    ("CCZ9", 579223, 6142268),
    ("PL", 583319, 6142980),
    ("LP", 576316, 6140002),
    ("EBLE", 585590.497, 6149915.441),
    ("PA", 569910, 6150918),
    ("EBCO", 580960.095, 6137944.447),
    ("PGZ", 579291, 6150587),
    ("CCZ9", 566360, 6144490),
    ("MB", 573309, 6142960),
    ("PC", 576700, 6133876),
    ("EBSV", 559186.349, 6150356.228)
]

# Datos de precipitación (simulados aquí, reemplázalos por tus datos reales)
acum_mensual_equipo_valido = np.random.rand(len(ubicaciones))  # Esto es solo un ejemplo

# Nombres de equipos válidos
nombres_equipos_validos = [ubicacion[0] for ubicacion in ubicaciones]

print(nombres_equipos_validos)
# Ubicaciones ordenadas
ubicaciones_ordenadas = []

for equipo in nombres_equipos_validos:
    for ubicacion in ubicaciones:
        if equipo == ubicacion[0]:
            ubicaciones_ordenadas.append([equipo, ubicacion[1], ubicacion[2]])

ubicaciones_ordenadas = np.array(ubicaciones_ordenadas).T
print(ubicaciones_ordenadas.shape)

# Extraer las coordenadas X e Y
X = np.array(ubicaciones_ordenadas[1, :], dtype=float)  # Coordenadas X UTM 21S (en metros)
Y = np.array(ubicaciones_ordenadas[2, :], dtype=float)  # Coordenadas Y UTM 21S (en metros)

# Valores de precipitación Z
Z = acum_mensual_equipo_valido  # Asegúrate de que acum_mensual_equipo_valido sea un arreglo de valores numéricos

# Crear una malla de puntos para la interpolación
xq = np.linspace(551332.763, 590932.763, 100)  # Crear un vector de puntos de consulta X
yq = np.linspace(6131816.936, 6160416.936, 100)  # Crear un vector de puntos de consulta Y
Xq, Yq = np.meshgrid(xq, yq)  # Crear una malla de consulta

# Interpolación IDW
power = 2  # Valor del exponente para IDW
Zq = np.zeros(Xq.shape)  # Inicializar la matriz de resultados

for i in range(Xq.size):
    # Calcular las distancias desde el punto de consulta a todos los puntos de datos
    distances = np.sqrt((X - Xq.flatten()[i])**2 + (Y - Yq.flatten()[i])**2)  # Distancias
    weights = 1 / distances**power  # Pesos IDW
    weights[distances == 0] = np.inf  # Evitar división por cero asignando peso infinito si la distancia es 0
    Zq.flatten()[i] = np.sum(weights * Z) / np.sum(weights)  # Cálculo del valor interpolado

# Determinar el rango de Z
minZ = np.min(Zq)  # Valor mínimo
maxZ = np.max(Zq)  # Valor máximo
rango = maxZ - minZ  # Calcular el rango

# Calcular un múltiplo apropiado
num_niveles = 6  # Número de niveles deseados
multiplo = np.ceil(rango / num_niveles)  # Calcular el múltiplo

# Generar los niveles automáticamente
nivel = np.arange(np.floor(minZ / multiplo) * multiplo, np.ceil(maxZ / multiplo) * multiplo, multiplo)

# Asegurarse de que haya al menos 5 niveles
if len(nivel) < 6:
    raise ValueError("No hay suficientes niveles para crear el mapa de isoyetas.")

# Graficar el mapa de isoyetas
plt.figure()
plt.contourf(Xq, Yq, Zq, levels=nivel, cmap='Blues')  # Crear el mapa de isoyetas con los niveles definidos
plt.colorbar()

# Agregar las etiquetas de los contornos
CS = plt.contour(Xq, Yq, Zq, levels=nivel, colors='black')
plt.clabel(CS, inline=True, fontsize=8)

# Título del gráfico
plt.title('Mapa de Isoyetas usando IDW')

# Cargar la imagen del mapa de fondo
mapa_fondo = plt.imread('./MAPA GENERAL MONTEVIDEO.png')  # Asegúrate de que este archivo esté en la misma carpeta

# Mostrar el mapa de fondo
plt.imshow(mapa_fondo, extent=[551332.763, 590932.763, 6131816.936, 6160416.936], alpha=0.3)

# Graficar las estaciones en rojo
plt.scatter(X, Y, color='r', label='Estaciones')

# Etiquetas de las estaciones
for i in range(len(X)):
    plt.text(X[i] - 100, Y[i] - 100, nombres_equipos_validos[i], fontsize=8, color='b', 
             backgroundcolor='white')

plt.axis('equal')
plt.show()
