from tkinter import *
import tkinter as tk
import tkinter
from tkinter import messagebox
from tkinter import filedialog
from Funciones import *
from tkinter import *
import tkinter as tk
from tkinter import messagebox
from Funciones import *
from tkinter import *
import tkinter as tk
from tkinter import messagebox
from Funciones import *

# Diccionario para guardar el estado de los checkboxes
estado_selecciones = {}

# Variable global para almacenar el archivo seleccionado
archivo_seleccionado = None

# Función que guarda el estado de los checkboxes
def guardar_selecciones(checkboxes):
    global estado_selecciones
    for pluvio, var in checkboxes.items():
        estado_selecciones[pluvio] = var.get()  # Guardamos el estado de cada checkbox

# Función que se ejecuta cuando el usuario da click en "Procesar"
def procesar_seleccionados():
    seleccionados = []
    for pluvio, var in checkboxes.items():
        if var.get() == 1:
            seleccionados.append(pluvio)
    
    if not seleccionados:
        messagebox.showwarning("Advertencia", "Debe seleccionar al menos un pluviómetro.")
    else:
        print("Pluviómetros seleccionados:", seleccionados)
        # Aquí puedes llamar a la función que procesa los pluviómetros seleccionados
        # por ejemplo: procesar_pluviometros(seleccionados)

# Función para habilitar el botón "Comenzar" si hay una ruta seleccionada
def habilitar_boton_comenzar():
    if archivo_text.get():  # Si hay texto en el campo de archivo (es decir, si se ha seleccionado un archivo)
        comenzar_btn.config(state=NORMAL)  # Activar el botón "Comenzar"
    else:
        comenzar_btn.config(state=DISABLED)  # De lo contrario, desactivar el botón "Comenzar"

# Función para regresar a la ventana anterior (ventana de inicio)
def regresar_inicio(root):
    guardar_selecciones(checkboxes)  # Guardamos las selecciones antes de cerrar la ventana
    root.destroy()  # Cierra la ventana actual
    crear_ventana_inicio()  # Vuelve a crear la ventana de inicio

# Función que se ejecuta cuando el usuario selecciona un archivo
def seleccionar_archivo():
    archivo = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if archivo:
        archivo_text.delete(0, END)  # Borrar texto previo
        archivo_text.insert(0, archivo)  # Rellenar con la ruta seleccionada
        comenzar_btn.config(state=NORMAL)  # Activar botón "Comenzar"
        global archivo_seleccionado
        archivo_seleccionado = archivo  # Guardar la ruta seleccionada en una variable global

# Función para crear la ventana de inicio
def crear_ventana_inicio():
    global archivo_seleccionado
    inicio = tk.Tk()

    # Centrar la ventana
    screen_width = inicio.winfo_screenwidth()
    screen_height = inicio.winfo_screenheight()
    window_width = 500  # Ancho de la ventana
    window_height = 200  # Alto de la ventana
    position_top = int(screen_height / 2 - window_height / 2)
    position_left = int(screen_width / 2 - window_width / 2)
    
    inicio.geometry(f'{window_width}x{window_height}+{position_left}+{position_top}')
    inicio.title("Ventana de Inicio")

    # Etiqueta para seleccionar archivo
    archivo_label = tk.Label(inicio, text="Seleccionar archivo CSV: ", font=("Arial", 12, "bold"))
    archivo_label.pack(pady=10)

    # Crear un frame para la selección de archivo
    archivo_frame = tk.Frame(inicio)
    archivo_frame.pack(pady=10)

    # Caja de texto para mostrar la ruta del archivo
    global archivo_text
    archivo_text = tk.Entry(archivo_frame, font=("Arial", 12), width=40)
    archivo_text.pack(side=LEFT, padx=5)

    # Si ya se ha seleccionado un archivo previamente, restauramos la ruta
    if archivo_seleccionado:
        archivo_text.insert(0, archivo_seleccionado)
    
    # Botón para seleccionar el archivo
    archivo_btn = tk.Button(archivo_frame, text=" ... ", command=seleccionar_archivo, font=("Arial", 8, "bold"))
    archivo_btn.pack(side=LEFT)

    # Botón para comenzar
    global comenzar_btn
    comenzar_btn = tk.Button(inicio, text="Siguiente", command=lambda: [inicio.destroy(), crear_interfaz(leo_archivo(archivo_seleccionado))], font=("Arial", 12, "bold"), state=DISABLED)
    comenzar_btn.pack(pady=20)

    # Verificar si hay archivo seleccionado para habilitar el botón al inicio
    habilitar_boton_comenzar()
    
    inicio.mainloop()

# Función para crear la interfaz de selección de pluviómetros
def crear_interfaz(datos):
    root = tk.Tk()

    # Centrar la ventana
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 560  # Ancho de la ventana
    window_height = 400  # Alto de la ventana
    position_top = int(screen_height / 2 - window_height / 2)
    position_left = int(screen_width / 2 - window_width / 2)
    
    root.geometry(f'{window_width}x{window_height}+{position_left}+{position_top}')
    root.title("Selección de Pluviómetros")

    # Obtener pluviómetros válidos
    pluvio_validos, pluvio_no_validos = obtener_pluviometros_validos(datos)

    global checkboxes
    checkboxes = {}

    # Crear un checkbox por cada pluviómetro válido en formato de cuadrícula
    row = 0  # Inicializamos en la fila 0
    col = 0  # Inicializamos en la columna 0

    for pluvio in pluvio_validos:
        # Recuperar el estado guardado o por defecto en 1 (seleccionado)
        estado = estado_selecciones.get(pluvio, 1)
        
        var = tk.IntVar(value=estado)  # Establecer como seleccionado por defecto
        checkboxes[pluvio] = var
        checkbutton = tk.Checkbutton(root, text=pluvio, variable=var, font=("Arial", 12, "bold"))  # Fuente más grande
        checkbutton.grid(row=row, column=col, padx=10, pady=10, sticky="w")  # Usamos grid

        # Actualizar las filas y columnas para la próxima iteración
        col += 1
        if col > 2:  # Si hemos alcanzado 3 columnas, pasamos a la siguiente fila
            col = 0
            row += 1

    # Botón para regresar a la ventana anterior
    regresar_btn = tk.Button(root, text="Regresar", command=lambda: regresar_inicio(root), font=("Arial", 12, "bold"))
    regresar_btn.grid(row=row + 1, column=0, pady=20)

    # Botón para procesar selección
    procesar_btn = tk.Button(root, text="Procesar", command=procesar_seleccionados, font=("Arial", 12, "bold"))
    procesar_btn.grid(row=row + 1, column=1, columnspan=5, pady=20)  # El botón ocupa toda la fila

    root.mainloop()

# Crear la ventana inicial (ventana de inicio)
crear_ventana_inicio()
