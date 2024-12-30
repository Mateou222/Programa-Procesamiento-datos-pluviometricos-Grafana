from tkinter import *
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from Funciones_basicas import *
from tkinter import *
from tkinter import messagebox
from Funciones_basicas import *
from tkinter import *
import tkinter as tk
from tkinter import messagebox
from Funciones_basicas import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Diccionario para guardar el estado de los checkboxes
estado_selecciones = {}
checkboxes = {}

# Variable global para almacenar el archivo seleccionado
archivo_seleccionado = None

# Función que actualiza el estado al seleccionar/deseleccionar un checkbox
def actualizar_seleccion(pluvio, var):
    estado_selecciones[pluvio] = var.get()
    
# Función para obtener pluviómetros seleccionados
def obtener_seleccionados():
    return [pluvio for pluvio, var in checkboxes.items() if var.get() == 1]

# Función que guarda el estado de los checkboxes
def guardar_selecciones(checkboxes):
    global estado_selecciones
    for pluvio, var in checkboxes.items():
        estado_selecciones[pluvio] = var.get()  # Guardamos el estado de cada checkbox

# Función que se ejecuta cuando el usuario selecciona un archivo
def seleccionar_archivo():
    archivo = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if archivo:
        archivo_text.delete(0, END)  # Borrar texto previo
        archivo_text.insert(0, archivo)  # Rellenar con la ruta seleccionada
        comenzar_btn.config(state=NORMAL)  # Activar botón "Comenzar"
        global archivo_seleccionado
        archivo_seleccionado = archivo  # Guardar la ruta seleccionada en una variable global
        habilitar_boton_comenzar()  # Habilitar el botón "Comenzar" si se ha seleccionado un archivo

# Función para habilitar el botón "Comenzar" si hay una ruta seleccionada
def habilitar_boton_comenzar():
    if archivo_text.get():  # Si hay texto en el campo de archivo (es decir, si se ha seleccionado un archivo)
        comenzar_btn.config(state=NORMAL)  # Activar el botón "Comenzar"
    else:
        comenzar_btn.config(state=DISABLED)  # De lo contrario, desactivar el botón "Comenzar"

# Función para regresar a la ventana de inicio desde la ventana principal
def regresar_inicio(root):
    global checkboxes
    checkboxes = {}  # Limpiar los checkboxes
    estado_selecciones.clear()  # Limpiar el diccionario de selecciones
    root.destroy()  # Cierra la ventana actual
    crear_ventana_inicio()  # Vuelve a crear la ventana de inicio
    
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
    comenzar_btn = tk.Button(inicio, text="Siguiente", command=lambda: [inicio.destroy(), crear_ventana_principal(leer_archivo(archivo_seleccionado))], font=("Arial", 12, "bold"), state=DISABLED)
    comenzar_btn.pack(pady=20)

    # Verificar si hay archivo seleccionado para habilitar el botón al inicio
    habilitar_boton_comenzar()
    
    inicio.mainloop()

# Función para mostrar la gráfica de lluvia instantánea
def mostrar_grafica_instantanea(lluvia_instantanea):
    seleccionados = obtener_seleccionados()
    if not seleccionados:
        messagebox.showwarning("Advertencia", "Seleccione al menos un pluviómetro.")
        return

    lluvia_filtrada = lluvia_instantanea[seleccionados]

    ventana_grafica = tk.Toplevel()
    ventana_grafica.attributes("-fullscreen", True)
    ventana_grafica.title("Gráfico de Lluvia Instantánea")

    fig = graficar_lluvia_instantanea(lluvia_filtrada)
    canvas = FigureCanvasTkAgg(fig, master=ventana_grafica)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    volver_btn = Button(ventana_grafica, text="Regresar", command=ventana_grafica.destroy, font=("Arial", 12, "bold"))
    volver_btn.pack(pady=10)

# Función para mostrar la gráfica de lluvia acumulada
def mostrar_grafica_acumulada(lluvia_acumulada):
    seleccionados = obtener_seleccionados()
    if not seleccionados:
        messagebox.showwarning("Advertencia", "Seleccione al menos un pluviómetro.")
        return

    lluvia_filtrada = lluvia_acumulada[seleccionados]

    ventana_grafica = tk.Toplevel()
    ventana_grafica.attributes("-fullscreen", True)
    ventana_grafica.title("Gráfico de Lluvia Acumulada")

    fig = graficar_lluvia_acumulado(lluvia_filtrada)
    canvas = FigureCanvasTkAgg(fig, master=ventana_grafica)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    volver_btn = Button(ventana_grafica, text="Regresar", command=ventana_grafica.destroy, font=("Arial", 12, "bold"))
    volver_btn.pack(pady=10)
    
# Función que se ejecuta cuando el usuario da click en "Procesar"
def procesar_seleccionados(lluvia_acumulada, lluvia_instantanea):
    seleccionados = obtener_seleccionados()
        
    if not seleccionados:
        messagebox.showwarning("Advertencia", "Seleccione al menos un pluviómetro.")
        return

    # Aquí puedes llamar a la función que procesa los pluviómetros seleccionados
    # por ejemplo: guardar las graficas y esas manos
    lluvia_filtrada_inst = lluvia_instantanea[seleccionados]
    
    fig_inst = graficar_lluvia_instantanea(lluvia_filtrada_inst)
    fig_inst.savefig("grafica instantaneas.jpg")
    
    lluvia_filtrada_acum = lluvia_acumulada[seleccionados]
    
    fig_acum = graficar_lluvia_acumulado(lluvia_filtrada_acum)
    fig_acum.savefig("grafica acumulado.jpg")
    
    messagebox.showinfo("Exito", "Procesado correctamente.")


# Función para crear la ventana interfaz principal
def crear_ventana_principal(datos):
    principal = tk.Tk()

    global checkboxes
    checkboxes = {}

    # Centrar la ventana
    screen_width = principal.winfo_screenwidth()
    screen_height = principal.winfo_screenheight()
    window_width = 1200  # Ancho de la ventana
    window_height = 850  # Alto de la ventana
    position_top = int(screen_height / 2 - window_height / 2)
    position_left = int(screen_width / 2 - window_width / 2)

    principal.geometry(f'{window_width}x{window_height}+{position_left}+{position_top}')
    principal.title("Ventana principal")

    # Parte superior: Información 
    info_frame = Frame(principal)
    info_frame.pack(side="top", fill="both", padx=20, pady=20)

    # Crear un frame para la información a la izquierda (pluviómetros y saltos)
    info_izquierda = Frame(info_frame)
    info_izquierda.pack(side="left", fill="both", padx=10)

    # Crear un frame para los porcentajes nulos a la derecha
    info_derecha = Frame(info_frame)
    info_derecha.pack(side="right", fill="both", padx=10)

    # Obtener pluviómetros válidos
    pluvio_validos, pluvio_no_validos = obtener_pluviometros_validos(datos)

    porcentaje_nulos = calcular_porcentaje_vacios(datos)

    acumulados = acumulado(datos)

    # Mostrar la información en el frame izquierdo
    info_label = tk.Label(info_izquierda, text="Información sobre los datos de precipitación:", 
                          font=("Arial", 16, "bold"))
    info_label.pack(fill="both", padx=10, pady=10)

    # Mostrar pluviómetros válidos
    pluvios_label = tk.Label(info_izquierda, text=f"Pluviómetros no válidos: {', '.join(pluvio_no_validos)}", 
                             font=("Arial", 12), justify="left")
    pluvios_label.pack(fill="both", padx=10, pady=5)

    # Mostrar saltos temporales
    saltos_label = tk.Label(info_izquierda, text="Saltos temporales detectados:", 
                            font=("Arial", 14, "bold"), justify="left")
    saltos_label.pack(fill="both", padx=10, pady=5)

    # Obtener los saltos temporales
    saltos = detectar_saltos_temporales(datos)
    
    # Mostrar los saltos temporales en el lado izquierdo
    for index, row in saltos.iterrows():
        columna = f"Pluviómetro: {row['Pluviómetro']}"
        valor = f"Inicio: {row['Inicio']} - Fin: {row['Fin']} - Duración: {row['Duración (min)']} min"
        
        # Creación de la etiqueta
        salto_label = tk.Label(info_izquierda, text=f"{columna}: {valor}", font=("Arial", 12), justify="left")
        salto_label.pack(fill="both", padx=20, pady=5)  # Aumentar el `padx` y `pady` para separación


    # Mostrar porcentaje de nulos en el frame derecho
    for index, row in porcentaje_nulos.iterrows():
        pluvio = row['Pluviómetro']  # Ajusta si el nombre de la columna es diferente
        porcentaje = row['Porcentaje_Nulos']  # Ajusta si el nombre de la columna es diferente
        nulos_label = tk.Label(info_derecha, text=f"{pluvio}: {porcentaje:.2f}% de valores nulos", 
                               font=("Arial", 12), justify="left")
        nulos_label.pack(fill="both", padx=10, pady=5)

    check_frame = Frame(principal)
    check_frame.pack()
    
    # Crear un checkbox por cada pluviómetro válido en formato de cuadrícula
    row, col = 0, 0
    for pluvio in pluvio_validos:
        estado = estado_selecciones.get(pluvio, 1)
        var = tk.IntVar(value=estado)
        checkboxes[pluvio] = var

        checkbutton = tk.Checkbutton(check_frame, text=pluvio, variable=var, font=("Arial", 12, "bold"),
                                     command=lambda p=pluvio, v=var: actualizar_seleccion(p, v))
        checkbutton.grid(row=row, column=col, padx=10, pady=10, sticky="w")

        col += 1
        if col > 6:
            col = 0
            row += 1
            
    # Parte inferior: Botones
    botonera_frame = Frame(principal)
    botonera_frame.pack(side="bottom", fill="x", pady=20)

    # Botón para regresar a la ventana de inicio
    volver_btn = tk.Button(botonera_frame, text="Reiniciar", command=lambda: regresar_inicio(principal), font=("Arial", 12, "bold"))
    volver_btn.pack(side="left", padx=50, pady=10)

    # Botón para mostrar la gráfica de lluvia instantánea
    grafica_instantanea_btn = Button(botonera_frame, text="Ver Gráfico Lluvia Instantánea", 
                                     command=lambda: mostrar_grafica_instantanea(instantaneo(datos)),
                                     font=("Arial", 12, "bold"))
    grafica_instantanea_btn.pack(side="left", padx=90, pady=10)

    # Botón para mostrar la gráfica de lluvia acumulada
    grafica_acumulada_btn = Button(botonera_frame, text="Ver Gráfico Lluvia Acumulada", 
                                   command=lambda: mostrar_grafica_acumulada(acumulados),
                                   font=("Arial", 12, "bold"))
    grafica_acumulada_btn.pack(side="left", padx=90, pady=10)

    # Botón para procesar selección
    procesar_btn = tk.Button(botonera_frame, text="Procesar", command=lambda: procesar_seleccionados(acumulados, instantaneo(datos)), font=("Arial", 12, "bold"))
    procesar_btn.pack(side="left", padx=50, pady=10)

    principal.mainloop()


# Crear la ventana inicial (ventana de inicio)
crear_ventana_inicio()
