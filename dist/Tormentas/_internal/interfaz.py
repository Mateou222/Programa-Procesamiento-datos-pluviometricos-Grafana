from tkinter import *
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
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
    ventana_inicio()  # Vuelve a crear la ventana de inicio
    
def iniciar_ventana_principal(archivo_seleccionado):
    datos = leer_archivo(archivo_seleccionado)
    
    global checkboxes
    checkboxes = {}
    
    pluvio_validos, pluvio_no_validos = obtener_pluviometros_validos(datos)

    global estado_selecciones
    # Inicializar estado_selecciones sin importar los valores previos
    estado_selecciones = {pluvio: 1 for pluvio in pluvio_validos}
     
    ventana_principal(datos)
    
# Función para crear la ventana de inicio
def ventana_inicio():
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
    comenzar_btn = tk.Button(inicio, text="Siguiente", command=lambda: [inicio.destroy(), iniciar_ventana_principal(archivo_seleccionado)], font=("Arial", 12, "bold"), state=DISABLED)
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
    
# Función para mostrar interfaz de selección y gráficas
def mostrar_interfaz_tr(lluvia_instantanea):
    seleccionados = obtener_seleccionados()
    
    if not seleccionados:
        messagebox.showwarning("Advertencia", "Seleccione al menos un pluviómetro.")
        return
    
    lluvia_filtrada = lluvia_instantanea[seleccionados]

    # Crear la ventana principal
    ventana_tr = tk.Toplevel()
    ventana_tr.attributes("-fullscreen", True)
    ventana_tr.title("Precipitación vs. Duración de Tormenta")
    
    # Frame izquierdo para selección
    frame_izq = tk.Frame(ventana_tr)
    frame_izq.pack(side="left", fill="y", padx=10, pady=200)

    # Frame izquierdo para selección
    frame_bottom = tk.Frame(ventana_tr)
    frame_bottom.pack(side="bottom", fill="y", padx=10, pady=10)
    
    # Checkboxes para TRs
    lista_tr = [tk.IntVar(value=v) for v in [1, 1, 1, 1, 0, 1, 0]]
    tr_labels = ["TR 2 años", "TR 5 años", "TR 10 años", "TR 20 años", "TR 25 años", "TR 50 años", "TR 100 años"]
    tk.Label(frame_izq, text="Seleccionar TRs").pack(pady=10)
    for i, tr in enumerate(tr_labels):
        tk.Checkbutton(frame_izq, text=tr, variable=lista_tr[i]).pack(anchor="w")

    # Frame derecho para gráfica
    frame_graficas = tk.Frame(ventana_tr)
    frame_graficas.pack(side="right", expand=True, fill="both", padx=10, pady=10)

    # Canvas para la gráfica
    canvas = tk.Canvas(frame_graficas)
    canvas.pack(fill="both", expand=True)
    
    # Crear la etiqueta
    tk.Label(frame_izq, text="Seleccionar Limites Precipitacion").pack(pady=5)
    # Crear el Entry para que el usuario ingrese el valor
    limite_selector = tk.Entry(frame_izq)
    limite_selector.pack(pady=5)   
    # Establecer un valor predeterminado (si lo deseas)
    limite_selector.insert(0, 150)  # Establece el primer valor 
    
    tk.Label(frame_izq, text="Limite Grafica ampliada").pack(pady=5)
    # Crear el Entry para que el usuario ingrese el valor
    limite_selector_ampliada = tk.Entry(frame_izq)
    limite_selector_ampliada.pack(pady=5)   
    # Establecer un valor predeterminado (si lo deseas)
    limite_selector_ampliada.insert(0, 80)  # Establece el primer valor 
    
    tk.Label(frame_izq, text="Seleccionar Pluviómetro").pack(pady=5)
    pluv_selector = ttk.Combobox(frame_izq, values=list(lluvia_filtrada.columns))
    pluv_selector.pack(pady=5)
    pluv_selector.set(lluvia_filtrada.columns[0])

    # Variable para rastrear el tipo de gráfica mostrada
    ultima_grafica = "ninguna"  # Puede ser "pluviómetro" o "total"
    
    # Función para actualizar gráfica
    def graficar_pluv():
        global ultima_grafica
        
        pluvio = pluv_selector.get()
        precipitaciones = calcular_precipitacion_pluvio(lluvia_filtrada, pluvio)
        fig = grafica_tr([var.get() for var in lista_tr], precipitaciones, float(limite_selector.get()), 1480, pluvio, "Precipitación vs. Duración de Tormenta")
        fig_ampliada  = grafica_tr([var.get() for var in lista_tr], precipitaciones, float(limite_selector_ampliada.get()), 120, pluvio, "Grafica ampliada")

        for widget in frame_graficas.winfo_children():
            widget.destroy()

        canvas1 = FigureCanvasTkAgg(fig, master=frame_graficas)
        canvas1.get_tk_widget().pack(fill="both", expand=True)
        canvas1.draw()
        
        canvas2 = FigureCanvasTkAgg(fig_ampliada, master=frame_graficas)
        canvas2.get_tk_widget().pack(fill="both", expand=True)
        canvas2.draw()
        
        # Actualizamos la variable de estado
        ultima_grafica = "pluviómetro"

    # Botón de actualización de gráfica
    tk.Button(frame_izq, text="Graficar pluviometro", command=graficar_pluv, font=("Arial", 10, "bold")).pack(pady=10)

    # Botón para mostrar todos los pluviómetros
    def graficar_todos():
        global ultima_grafica
        
        precipitaciones = calcular_precipitacion_para_tr(lluvia_filtrada)
        fig = grafica_tr([var.get() for var in lista_tr], precipitaciones, float(limite_selector.get()), 1480, "RHM", "Precipitación vs. Duración de Tormenta")
        fig_ampliada  = grafica_tr([var.get() for var in lista_tr], precipitaciones, float(limite_selector_ampliada.get()), 120, "RHM", "Grafica ampliada")

        for widget in frame_graficas.winfo_children():
            widget.destroy()

        canvas1 = FigureCanvasTkAgg(fig, master=frame_graficas)
        canvas1.get_tk_widget().pack(fill="both", expand=True)
        canvas1.draw()
        
        canvas2 = FigureCanvasTkAgg(fig_ampliada, master=frame_graficas)
        canvas2.get_tk_widget().pack(fill="both", expand=True)
        canvas2.draw()
        # Actualizamos la variable de estado
        ultima_grafica = "total"

    graficar_todos()
    
    def guardar_graficas():
        # Cuadro de diálogo para seleccionar directorio y nombre del archivo
        directorio = filedialog.askdirectory(title="Selecciona un directorio para guardar las gráficas")
        ventana_tr.lift()
        
        if directorio:
            # Determinar el nombre del archivo dependiendo del tipo de gráfica mostrada
            if ultima_grafica == "pluviómetro":
                pluvio = pluv_selector.get()
                nombre_archivo = f"grafica_{pluvio}.png"
                nombre_archivo_ampliada = f"grafica_ampliada_{pluvio}.png"
                precipitaciones = calcular_precipitacion_pluvio(lluvia_filtrada, pluvio)
                fig = grafica_tr([var.get() for var in lista_tr], precipitaciones, 
                                float(limite_selector.get()), 1480, pluvio, "Precipitación vs. Duración de Tormenta")
                fig_ampliada = grafica_tr([var.get() for var in lista_tr], precipitaciones, 
                                      float(limite_selector_ampliada.get()), 120, pluvio, "Grafica ampliada")
            else:
                nombre_archivo = "grafica_total.png"
                nombre_archivo_ampliada = "grafica_ampliada_total.png"
                precipitaciones = calcular_precipitacion_para_tr(lluvia_filtrada)
                fig = grafica_tr([var.get() for var in lista_tr], precipitaciones, float(limite_selector.get()), 1480, "RHM", "Precipitación vs. Duración de Tormenta")
                fig_ampliada  = grafica_tr([var.get() for var in lista_tr], precipitaciones, float(limite_selector_ampliada.get()), 120, "RHM", "Grafica ampliada")

            # Guardar la primera gráfica
            fig.savefig(f"{directorio}/{nombre_archivo}")

            # Guardar la gráfica ampliada
            
            fig_ampliada.savefig(f"{directorio}/{nombre_archivo_ampliada}")
            
            messagebox.showinfo("Éxito", "Las gráficas se han guardado correctamente.")
            ventana_tr.lift()
    
    tk.Button(frame_izq, text="Graficar Todos", command=graficar_todos, font=("Arial", 10, "bold")).pack(pady=5)
    
    # Botón para regresar (cerrar la ventana de gráfica)
    tk.Button(frame_bottom, text="Regresar", command=ventana_tr.destroy, font=("Arial", 12, "bold")).pack(side="left", padx=30)
    
    # Botón para regresar (cerrar la ventana de gráfica)
    tk.Button(frame_bottom, text="Guardar graficas", command=guardar_graficas, font=("Arial", 12, "bold")).pack(side="left", pady=20)

    ventana_tr.mainloop()

    
# Función que se ejecuta cuando el usuario da click en "Procesar"
def procesar_seleccionados(lluvia_acumulada, lluvia_instantanea):
    seleccionados = obtener_seleccionados()
        
    if not seleccionados:
        messagebox.showwarning("Advertencia", "Seleccione al menos un pluviómetro.")
        return

    # Aquí puedes llamar a la función que procesa los pluviómetros seleccionados
    # por ejemplo: guardar las graficas y esas manos
    lluvia_filtrada_inst = lluvia_instantanea[seleccionados]
    
    # Cuadro de diálogo para seleccionar directorio y nombre del archivo
    directorio = filedialog.askdirectory(title="Selecciona un directorio para guardar las gráficas")
        
    fig_inst = graficar_lluvia_instantanea(lluvia_filtrada_inst)
    fig_inst.savefig(f"{directorio}/grafica instantaneas.png")
    
    lluvia_filtrada_acum = lluvia_acumulada[seleccionados]
    
    fig_acum = graficar_lluvia_acumulado(lluvia_filtrada_acum)
    # Guardar la primera gráfica
    fig_acum.savefig(f"{directorio}/grafica acumulado.png")
    
    messagebox.showinfo("Exito", "Procesado correctamente.")


# Función para crear la ventana interfaz principal
def ventana_principal(datos):
    principal = tk.Tk()

    global checkboxes

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
    saltos = detectar_saltos_temporales(datos[pluvio_validos])
    
    # Mostrar los saltos temporales en el lado izquierdo
    for index, row in saltos.iterrows():
        columna = f"{row['Pluviómetro']}"
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

    instantaneos = instantaneo(datos)
    
    # Botón para regresar a la ventana de inicio
    volver_btn = tk.Button(botonera_frame, text="Reiniciar", command=lambda: regresar_inicio(principal), font=("Arial", 12, "bold"))
    volver_btn.pack(side="left", padx=30, pady=10)

    # Botón para mostrar la gráfica de lluvia instantánea
    grafica_instantanea_btn = Button(botonera_frame, text="Ver Gráfico Lluvia Instantánea", 
                                     command=lambda: mostrar_grafica_instantanea(instantaneos),
                                     font=("Arial", 12, "bold"))
    grafica_instantanea_btn.pack(side="left", padx=40, pady=10)

    # Botón para mostrar la gráfica de lluvia acumulada
    grafica_acumulada_btn = Button(botonera_frame, text="Ver Gráfico Lluvia Acumulada", 
                                   command=lambda: mostrar_grafica_acumulada(acumulados),
                                   font=("Arial", 12, "bold"))
    grafica_acumulada_btn.pack(side="left", padx=40, pady=10)
    
    # Botón para mostrar la interfaz de tr
    grafica_acumulada_btn = Button(botonera_frame, text="Ver Gráfico Tr", 
                                   command=lambda: mostrar_interfaz_tr(instantaneos),
                                   font=("Arial", 12, "bold"))
    grafica_acumulada_btn.pack(side="left", padx=40, pady=10)

    # Botón para procesar selección
    procesar_btn = tk.Button(botonera_frame, text="Guardar Graficas", command=lambda: procesar_seleccionados(acumulados, instantaneos), font=("Arial", 12, "bold"))
    procesar_btn.pack(side="left", padx=30, pady=10)

    principal.mainloop()


# Crear la ventana inicial (ventana de inicio)
ventana_inicio()
