from tkinter import *
import tkinter as tk
import tkinter
from tkinter import messagebox
from Funciones import *

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

# Función para crear la interfaz
def crear_interfaz(datos):
    root = tk.Tk()
    
    # Centrar la ventana
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 600  # Ancho de la ventana
    window_height = 400  # Alto de la ventana
    position_top = int(screen_height / 2 - window_height / 2)
    position_left = int(screen_width / 2 - window_width / 2)
    
    root.geometry(f'{window_width}x{window_height}+{position_left}+{position_top}')
    root.title("Selección de Pluviómetros")

    # Obtener pluviómetros válidos
    pluvio_validos = obtener_pluviometros_validos(datos)

    global checkboxes
    checkboxes = {}

    # Crear un checkbox por cada pluviómetro válido en formato de cuadrícula
    row = 0  # Inicializamos en la fila 0
    col = 0  # Inicializamos en la columna 0

    for pluvio in pluvio_validos:
        var = tk.IntVar(value=1)  # Establecer como seleccionado por defecto
        checkboxes[pluvio] = var
        checkbutton = tk.Checkbutton(root, text=pluvio, variable=var, font=("Arial", 12, "bold"))  # Fuente más grande
        checkbutton.grid(row=row, column=col, padx=10, pady=10, sticky="w")  # Usamos grid

        # Actualizar las filas y columnas para la próxima iteración
        col += 1
        if col > 2:  # Si hemos alcanzado 3 columnas, pasamos a la siguiente fila
            col = 0
            row += 1

    # Botón para procesar selección
    procesar_btn = tk.Button(root, text="Procesar", command=procesar_seleccionados, font=("Arial", 12, "bold"))
    procesar_btn.grid(row=row + 1, column=0, columnspan=5, pady=20)  # El botón ocupa toda la fila

    root.mainloop()
    
# Crear la interfaz
crear_interfaz(leo_archivo())