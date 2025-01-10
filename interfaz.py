from tkinter import *
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
  
from Funciones_basicas import *
from Funciones_tormenta import *
from Funciones_mensual import *
    
class VentanaInicio(tk.Tk):
    def __init__(self, archivo_seleccionado, analisis_seleccionado_guardado):
        super().__init__()
        self.archivo_seleccionado = archivo_seleccionado
        self.analisis_seleccionado_guardado = analisis_seleccionado_guardado
        self.archivo_validador_seleccionado = ""
        self.archivo_inumet_seleccionado = ""
        self.title("Ventana de Inicio")
        self.geometry(self.centrar_ventana(500, 350))
        
        self.archivo_principal_text = None
        self.archivo_validador_text = None
        self.archivo_inumet_text = None
        self.analisis_seleccionado = None
        self.comenzar_btn = None
        
        
        self.crear_widgets()
        self.mainloop()

    def centrar_ventana(self, ancho, alto):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        position_top = int(screen_height / 2 - alto / 2)
        position_left = int(screen_width / 2 - ancho / 2)
        return f'{ancho}x{alto}+{position_left}+{position_top}'

    def crear_widgets(self):
        # Frame para seleccionar archivo principal
        archivo_frame = tk.Frame(self)
        archivo_frame.pack(pady=5)
        tk.Label(archivo_frame, text="Seleccionar archivo CSV: ", font=("Arial", 10, "bold")).pack(pady=5)
        
        self.archivo_principal_text = tk.Entry(archivo_frame, font=("Arial", 12), width=40)
        self.archivo_principal_text.pack(side=tk.LEFT, padx=5)
        
        if self.archivo_seleccionado:
            self.archivo_principal_text.insert(0, self.archivo_seleccionado)
        
        tk.Button(archivo_frame, text=" ... ", command=self.seleccionar_archivo_principal, font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        # Selección de tipo de análisis
        seleccion = tk.Frame(self)
        seleccion.pack(pady=5)
        tk.Label(seleccion, text="Seleccionar Tipo de análisis", font=("Arial", 10, "bold")).pack(pady=5)
        
        self.analisis_seleccionado = ttk.Combobox(seleccion, values=["Tormenta", "Mensual"])
        self.analisis_seleccionado.pack(pady=5)
        if self.analisis_seleccionado_guardado:
            self.analisis_seleccionado.set(self.analisis_seleccionado_guardado)
        else:    
            self.analisis_seleccionado.set("")
        
        self.analisis_seleccionado.bind("<<ComboboxSelected>>", self.habilitar_boton_comenzar)

        # Archivo validador
        archivo_validador_frame = tk.Frame(self)
        archivo_validador_frame.pack(pady=5)
        tk.Label(archivo_validador_frame, text="Seleccionar archivo CSV del validador: ", font=("Arial", 10, "bold")).pack(pady=5)
        
        self.archivo_validador_text = tk.Entry(archivo_validador_frame, font=("Arial", 12), width=40)
        self.archivo_validador_text.pack(side=tk.LEFT, padx=5)
        tk.Button(archivo_validador_frame, text=" ... ", command=self.seleccionar_archivo_verificador, font=("Arial", 10, "bold")).pack(side=tk.LEFT)

        # Archivo INUMET
        archivo_inumet_frame = tk.Frame(self)
        archivo_inumet_frame.pack(pady=5)
        tk.Label(archivo_inumet_frame, text="Seleccionar archivo CSV de INUMET: ", font=("Arial", 10, "bold")).pack(pady=5)
        
        self.archivo_inumet_text = tk.Entry(archivo_inumet_frame, font=("Arial", 12), width=40)
        self.archivo_inumet_text.pack(side=tk.LEFT, padx=5)
        
        if self.archivo_inumet_text:
            self.archivo_inumet_text.insert(0, self.archivo_inumet_seleccionado)
        
        tk.Button(archivo_inumet_frame, text=" ... ", command=self.seleccionar_archivo_inumet, font=("Arial", 10, "bold")).pack(side=tk.LEFT)

        # Botón Siguiente
        self.comenzar_btn = tk.Button(self, text="Siguiente", command=self.iniciar_ventanas, font=("Arial", 12, "bold"), state=tk.DISABLED)
        self.comenzar_btn.pack(pady=5)

        self.archivo_principal_text.bind("<FocusOut>", self.habilitar_boton_comenzar)
        self.archivo_inumet_text.bind("<FocusOut>", self.habilitar_boton_comenzar)
        
        self.habilitar_boton_comenzar()

    def seleccionar_archivo_principal(self):
        archivo = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if archivo:
            self.archivo_principal_text.delete(0, END)  # Borrar texto previo
            self.archivo_principal_text.insert(0, archivo)  # Rellenar con la ruta seleccionada
            self.archivo_seleccionado = archivo  # Guardar la ruta seleccionada en una variable global
            self.habilitar_boton_comenzar()  # Habilitar el botón "Comenzar" si se ha seleccionado un archivo

    def seleccionar_archivo_verificador(self):
        archivo = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if archivo:
            self.archivo_validador_text.delete(0, END)  # Borrar texto previo
            self.archivo_validador_text.insert(0, archivo)  # Rellenar con la ruta seleccionada
            self.archivo_validador_seleccionado = archivo  # Guardar la ruta seleccionada en una variable global

    def seleccionar_archivo_inumet(self):
        archivo = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if archivo:
            self.archivo_inumet_text.delete(0, END)  # Borrar texto previo
            self.archivo_inumet_text.insert(0, archivo)  # Rellenar con la ruta seleccionada
            self.archivo_inumet_seleccionado = archivo  # Guardar la ruta seleccionada en una variable global
            self.habilitar_boton_comenzar()

    def habilitar_boton_comenzar(self, event=None):
        if self.archivo_principal_text.get() and self.analisis_seleccionado.get() == "Tormenta":  # Si hay texto en el campo de archivo (es decir, si se ha seleccionado un archivo)
            self.comenzar_btn.config(state=NORMAL)  # Activar el botón "Comenzar"
        else:
            if self.analisis_seleccionado.get() == "Mensual" and self.archivo_principal_text.get() and self.archivo_inumet_text.get():
                self.comenzar_btn.config(state=NORMAL)  # Activar el botón "Comenzar
            else:
                self.comenzar_btn.config(state=DISABLED)  # De lo contrario, desactivar el botón "Comenzar"     

        
    def iniciar_ventanas(self):
        self.df_datos = leer_archivo_principal(self.archivo_seleccionado)
        
        if self.archivo_validador_seleccionado:
            self.df_datos = leer_archivo_verificador(self.archivo_validador_seleccionado, self.df_datos)
            
        if self.archivo_inumet_seleccionado:
            df_instantaneo = calcular_instantaneos(self.df_datos)
            self.df_acumulados_diarios = calcular_acumulados_diarios(df_instantaneo)
            self.df_acumulados_diarios = leer_archivo_inumet(self.archivo_inumet_seleccionado, self.
                                                             df_acumulados_diarios)
        
        self.df_datos_original = self.df_datos
                
        self.analisis_seleccionado_guardado = self.analisis_seleccionado.get()
        
        if self.analisis_seleccionado.get()== "Tormenta":
            self.cerrar_ventana()
            return VentanaLimiteTemporal(self)
        if self.analisis_seleccionado.get()=="Mensual":
            self.cerrar_ventana()
            return VentanaPrincipalMensual(self)

    def cerrar_ventana(self):
        self.withdraw()
        
class VentanaLimiteTemporal(tk.Toplevel):
    def __init__(self, ventana_principal):
        super().__init__()
        self.ventana_principal = ventana_principal
        
        pluvio_validos, pluvio_no_validos = obtener_pluviometros_validos(self.ventana_principal.df_datos)
        df_lluvia_instantanea = calcular_instantaneos(self.ventana_principal.df_datos_original)

        self.lluvia_filtrada = df_lluvia_instantanea[pluvio_validos]
        
        self.title("Ventana limite temporal")
        self.state('zoomed')
        
        self.limite_inf_selector = None
        self.limite_sup_selector = None
        self.frame_grafica = None
        
        self.crear_widgets()
        self.actualizar_grafica()
        
    def crear_widgets(self):
        # Frame para gráfica
        self.frame_grafica = tk.Frame(self)
        self.frame_grafica.pack(side="top", expand=True, fill="both", padx=10)
        
        # Frame establecer limites
        frame_limites = tk.Frame(self)
        frame_limites.pack(side="bottom", fill="y", padx=10, pady=10)

        tk.Button(frame_limites, text="Reiniciar", command=self.regresar_inicio, font=("Arial", 10, "bold")).pack(side="left", pady=10, padx=10)
        
        tk.Label(frame_limites, text="Seleccionar Limites:").pack(side="left", pady=10)
        
        self.limite_inf_selector = tk.Entry(frame_limites)
        self.limite_inf_selector.pack(side="left", pady=10, padx=10)
        self.limite_inf_selector.insert(0, self.ventana_principal.df_datos.index.min())
        
        self.limite_sup_selector = tk.Entry(frame_limites)
        self.limite_sup_selector.pack(side="left", pady=10, padx=10)
        self.limite_sup_selector.insert(0, self.ventana_principal.df_datos.index.max())
        
        tk.Button(frame_limites, text="Aplicar", command=self.actualizar_grafica, font=("Arial", 10, "bold")).pack(side="left", pady=10, padx=10)
        
        tk.Button(frame_limites, text="Siguiente", command=self.actualizar_df_datos, font=("Arial", 10, "bold")).pack(side="left", pady=10, padx=10)

    def actualizar_grafica(self):
        if self.validar_datos():
            lluvia_limitada_temp = limitar_df_temporal(self.lluvia_filtrada, 
                                                       self.limite_inf_selector.get(), 
                                                       self.limite_sup_selector.get())
            fig = graficar_lluvia_instantanea_tormenta(lluvia_limitada_temp)
            
            for widget in self.frame_grafica.winfo_children():
                widget.destroy()
            
            canvas = FigureCanvasTkAgg(fig, master=self.frame_grafica)
            canvas.get_tk_widget().pack(fill="both", expand=True)
            canvas.draw()

    def validar_datos(self):
        try:
            limite_inf = pd.to_datetime(self.limite_inf_selector.get())
            limite_sup = pd.to_datetime(self.limite_sup_selector.get())
            
            if limite_inf < self.ventana_principal.df_datos_original.index.min():
                messagebox.showwarning("Advertencia", "La fecha mínima seleccionada excede el límite.")
                self.limite_inf_selector.delete(0, tk.END)
                self.limite_inf_selector.insert(0, self.ventana_principal.df_datos.index.min())
                return False
            
            if limite_sup > self.ventana_principal.df_datos_original.index.max():
                messagebox.showwarning("Advertencia", "La fecha máxima seleccionada excede el límite.")
                self.limite_sup_selector.delete(0, tk.END)
                self.limite_sup_selector.insert(0, self.ventana_principal.df_datos.index.max())
                return False
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error validando fechas: {str(e)}")
            return False

    def actualizar_df_datos(self):
        if self.validar_datos():
            self.ventana_principal.df_datos = limitar_df_temporal(self.ventana_principal.df_datos_original, 
                                                   self.limite_inf_selector.get(), 
                                                   self.limite_sup_selector.get())
            self.proxima_ventana_tormenta()

    def regresar_inicio(self):
        self.cerrar_ventana()
        self.ventana_principal.deiconify()
        
    def proxima_ventana_tormenta(self):
        self.cerrar_ventana()
        VentanaPrincipalTormenta(self.ventana_principal)
        
    def cerrar_ventana(self):
        self.destroy()

class MostrarGrafica(tk.Toplevel):
    def __init__(self, grafica):
        super().__init__()
                
        self.state('zoomed')
        
        canvas = FigureCanvasTkAgg(grafica, master=self)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        volver_btn = Button(self, text="Regresar", command=self.destroy, font=("Arial", 10, "bold"))
        volver_btn.pack(pady=10)

class VentanaPrincipalTormenta(tk.Toplevel):
    def __init__(self, ventana_principal):
        super().__init__()
        self.ventana_principal = ventana_principal
        
        self.title("Ventana principal")
        self.state('zoomed')
        
        self.pluvio_validos, self.pluvio_no_validos = obtener_pluviometros_validos(self.ventana_principal.df_datos)
        self.df_acumulados = acumulados(self.ventana_principal.df_datos)
        self.df_acumulados_total = acumulado_total(self.df_acumulados)
        self.df_instantaneos = calcular_instantaneos(self.ventana_principal.df_datos)
        self.df_saltos_maximos, self.df_saltos = detectar_saltos_temporales(self.ventana_principal.df_datos[self.pluvio_validos])
        self.df_porcentaje_vacio = calcular_porcentaje_vacios(self.ventana_principal.df_datos[self.pluvio_validos])
          # Lista que almacena los pluviómetros seleccionados

        self.crear_interfaz()

    # Función para mostrar interfaz de selección y gráficas
    def mostrar_interfaz_tr_tormenta(self):    
        """
        if not self.seleccionados:
            messagebox.showwarning("Advertencia", "Seleccione al menos un pluviómetro.")
            return
        
        lluvia_filtrada = self.df_instantaneos[self.seleccionados]
        """    
        lluvia_filtrada = self.df_instantaneos
        
        # Crear la ventana principal
        ventana_tr = tk.Toplevel()
        ventana_tr.state('zoomed')
        ventana_tr.title("Precipitación vs. Duración de Tormenta")
        
        # Frame izquierdo para selección
        frame_izq = tk.Frame(ventana_tr)
        frame_izq.pack(side="left", fill="y", padx=10, pady=10)

        # Frame izquierdo para selección
        frame_bottom = tk.Frame(ventana_tr)
        frame_bottom.pack(side="bottom", fill="y", padx=10, pady=10)
        
        # Checkboxes para TRs
        lista_tr = [tk.IntVar(value=v) for v in [1, 1, 1, 1, 0, 1, 0]]
        tr_labels = ["TR 2 años", "TR 5 años", "TR 10 años", "TR 20 años", "TR 25 años", "TR 50 años", "TR 100 años"]
        tk.Label(frame_izq, text="Seleccionar TRs", font="bold").pack(pady=10, padx=10)
        for i, tr in enumerate(tr_labels):
            tk.Checkbutton(frame_izq, text=tr, variable=lista_tr[i]).pack(anchor="w")
            
        tk.Label(frame_izq, text=" ", font="bold").pack()

        # Frame derecho para gráfica
        frame_graficas = tk.Frame(ventana_tr)
        frame_graficas.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        # Canvas para la gráfica
        canvas = tk.Canvas(frame_graficas)
        canvas.pack(fill="both", expand=True)
        
        # Crear la etiqueta
        tk.Label(frame_izq, text="Seleccionar Limites", font="bold").pack(pady=5)
        
        # Crear la etiqueta
        tk.Label(frame_izq, text="Precipitacion de al Grafica:").pack(pady=5)
        # Crear el Entry para que el usuario ingrese el valor
        limite_precipitacion_selector = tk.Entry(frame_izq)
        limite_precipitacion_selector.pack(pady=5)   
        # Establecer un valor predeterminado (si lo deseas)
        limite_precipitacion_selector.insert(0, 150)  # Establece el primer valor 
        
        tk.Label(frame_izq, text="Tiempo de la Grafica:").pack(pady=5)
        # Crear el Entry para que el usuario ingrese el valor
        limite_tiempo_selector = tk.Entry(frame_izq)
        limite_tiempo_selector.pack(pady=5)   
        # Establecer un valor predeterminado (si lo deseas)
        limite_tiempo_selector.insert(0, 1480)  # Establece el primer valor
        
        
        tk.Label(frame_izq, text="Precipitacion de la Grafica Ampliada:").pack(pady=5)
        # Crear el Entry para que el usuario ingrese el valor
        limite_precipitacion_selector_ampliada = tk.Entry(frame_izq)
        limite_precipitacion_selector_ampliada.pack(pady=5)   
        # Establecer un valor predeterminado (si lo deseas)
        limite_precipitacion_selector_ampliada.insert(0, 80)  # Establece el primer valor 
        
        tk.Label(frame_izq, text="Tiempo de la Grafica Ampliada:").pack(pady=5)
        # Crear el Entry para que el usuario ingrese el valor
        limite_tiempo_selector_ampliada = tk.Entry(frame_izq)
        limite_tiempo_selector_ampliada.pack(pady=5)   
        # Establecer un valor predeterminado (si lo deseas)
        limite_tiempo_selector_ampliada.insert(0, 120)  # Establece el primer valor
        
        # Variable para rastrear el tipo de gráfica mostrada
        ultima_grafica = "ninguna"  # Puede ser "pluviómetro" o "total"
        
        def actualizar_limites():
            if ultima_grafica == "pluviómetro":
                graficar_pluv()
            else:
                graficar_todos()
        
        # Botón de actualización de gráfica
        tk.Button(frame_izq, text="Actualizar limites", command=actualizar_limites, font=("Arial", 10, "bold"), width=15).pack(pady=10)
        
        tk.Label(frame_izq, text="Seleccionar Pluviómetro").pack(pady=5)
        pluv_selector = ttk.Combobox(frame_izq, values=list(lluvia_filtrada.columns))
        pluv_selector.pack(pady=5)
        pluv_selector.set(lluvia_filtrada.columns[0])
        
        # Función para actualizar gráfica
        def graficar_pluv(event=None):
            global ultima_grafica
            
            pluvio = pluv_selector.get()
            precipitaciones = calcular_precipitacion_pluvio(lluvia_filtrada, pluvio)
            fig = grafica_tr([var.get() for var in lista_tr], precipitaciones, float(limite_precipitacion_selector.get()), float(limite_tiempo_selector.get()), pluvio, "Precipitación vs. Duración de Tormenta")
            fig_ampliada  = grafica_tr([var.get() for var in lista_tr], precipitaciones, float(limite_precipitacion_selector_ampliada.get()), float(limite_tiempo_selector_ampliada.get()), pluvio, "Grafica ampliada")

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
            
        pluv_selector.bind("<<ComboboxSelected>>", graficar_pluv)

        # Botón para mostrar todos los pluviómetros
        def graficar_todos():
            global ultima_grafica
            
            precipitaciones = calcular_precipitacion_para_tr(lluvia_filtrada)
            fig = grafica_tr([var.get() for var in lista_tr], precipitaciones, float(limite_precipitacion_selector.get()), float(limite_tiempo_selector.get()), "RHM", "Precipitación vs. Duración de Tormenta")
            fig_ampliada  = grafica_tr([var.get() for var in lista_tr], precipitaciones, float(limite_precipitacion_selector_ampliada.get()), float(limite_tiempo_selector_ampliada.get()), "RHM", "Grafica ampliada")

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
                                    float(limite_precipitacion_selector.get()), float(limite_tiempo_selector.get()), pluvio, "Precipitación vs. Duración de Tormenta")
                    fig_ampliada = grafica_tr([var.get() for var in lista_tr], precipitaciones, 
                                        float(limite_precipitacion_selector_ampliada.get()), float(limite_tiempo_selector_ampliada.get()), pluvio, "Grafica ampliada")
                else:
                    nombre_archivo = "grafica_total.png"
                    nombre_archivo_ampliada = "grafica_ampliada_total.png"
                    precipitaciones = calcular_precipitacion_para_tr(lluvia_filtrada)
                    fig = grafica_tr([var.get() for var in lista_tr], precipitaciones, float(limite_precipitacion_selector.get()), float(limite_tiempo_selector.get()), "RHM", "Precipitación vs. Duración de Tormenta")
                    fig_ampliada  = grafica_tr([var.get() for var in lista_tr], precipitaciones, float(limite_precipitacion_selector_ampliada.get()), float(limite_tiempo_selector_ampliada.get()), "RHM", "Grafica ampliada")

                # Guardar la primera gráfica
                fig.savefig(f"{directorio}/{nombre_archivo}")

                # Guardar la gráfica ampliada
                
                fig_ampliada.savefig(f"{directorio}/{nombre_archivo_ampliada}")
                
                messagebox.showinfo("Éxito", "Las gráficas se han guardado correctamente.")
                ventana_tr.lift()
                
        tk.Button(frame_izq, text="Graficar Todos", command=graficar_todos, font=("Arial", 10, "bold"), width=15).pack(pady=10)
        
        # Botón para regresar (cerrar la ventana de gráfica)
        tk.Button(frame_bottom, text="Regresar",command= lambda: ventana_tr.destroy(), font=("Arial", 10, "bold")).pack(side="left", padx=20)
        
        # Botón para regresar (cerrar la ventana de gráfica)
        tk.Button(frame_bottom, text="Guardar graficas", command=guardar_graficas, font=("Arial", 10, "bold")).pack(side="left", pady=10)
    
    def mostrar_grafica_saltos(self, event):
        # Obtener el ítem que se seleccionó
        item = self.tabla.selection()  # Obtiene el ítem seleccionado
        if item:
            # Obtener los valores de la fila seleccionada
            item_values = self.tabla.item(item)["values"]
            grafica_value = item_values[-1]  # "Mostrar grafica" es la última columna
            if grafica_value == " ... ":
                ventana_grafica_saltos = tk.Toplevel()
                ventana_grafica_saltos.state('zoomed')
                ventana_grafica_saltos.title("Gráfico de Lluvia Acumulada")
                
                frame_combobox = tk.Frame(ventana_grafica_saltos)
                frame_combobox.pack(fill="x", pady=10)
                
                tk.Label(frame_combobox, text=f"Saltos detectados en el pluviometro {item_values[0]}", font=("Arial", 10, "bold")).pack()
                pluv_selector = ttk.Combobox(frame_combobox, values=["Todos los pluviometros", item_values[0]], width=30)
                pluv_selector.pack(pady=5)
                pluv_selector.configure(font=("Arial", 10))
                pluv_selector.set("Todos los pluviometros")
                
                # Frame derecho para gráfica
                frame_grafica = tk.Frame(ventana_grafica_saltos)
                frame_grafica.pack(expand=True, fill="both")

                def actualizar_grafica(event=None):
                    if pluv_selector.get()=="Todos los pluviometros":
                        fig = graficar_lluvia_con_saltos_tormenta(self.df_instantaneos, self.df_saltos, self.df_saltos_maximos, item_values[0], True)
                    else:
                        fig = graficar_lluvia_con_saltos_tormenta(self.df_instantaneos, self.df_saltos, self.df_saltos_maximos, item_values[0], False)
                        
                    for widget in frame_grafica.winfo_children():
                        widget.destroy()

                    canvas = FigureCanvasTkAgg(fig, master=frame_grafica)
                    canvas.get_tk_widget().pack(fill="both", expand=True)
                    canvas.draw()

                actualizar_grafica()
                
                pluv_selector.bind("<<ComboboxSelected>>", actualizar_grafica)

                volver_btn = Button(ventana_grafica_saltos, text="Regresar", command=ventana_grafica_saltos.destroy, font=("Arial", 10, "bold"))
                volver_btn.pack(pady=10)
    
    # Función que se ejecuta cuando el usuario da click en "Procesar"
    def guardar_graficas(self):       
        """
        if not self.seleccionados:
            messagebox.showwarning("Advertencia", "Seleccione al menos un pluviómetro.")
            return
        """
        # Aquí puedes llamar a la función que procesa los pluviómetros seleccionados
        # por ejemplo: guardar las graficas y esas manos
        #lluvia_filtrada_inst = self.df_instantaneos[self.seleccionados]
        lluvia_filtrada_inst = self.df_instantaneos
        
        # Cuadro de diálogo para seleccionar directorio y nombre del archivo
        directorio = filedialog.askdirectory(title="Selecciona un directorio para guardar las gráficas")
            
        fig_inst = graficar_lluvia_instantanea_tormenta(lluvia_filtrada_inst)
        fig_inst.savefig(f"{directorio}/grafica instantaneas.png")
        
        #lluvia_filtrada_acum = self.lluvia_acumulada[self.seleccionados]
        lluvia_filtrada_acum = self.lluvia_acumulada
        
        fig_acum = graficar_lluvia_acumulado_tormenta(lluvia_filtrada_acum)
        # Guardar la primera gráfica
        fig_acum.savefig(f"{directorio}/grafica acumulado.png")
        
        messagebox.showinfo("Exito", "Procesado correctamente.")


    def crear_interfaz(self):
        self.crear_info_frame()
        self.crear_botonera()

    def crear_info_frame(self):
        info_frame = Frame(self)
        info_frame.pack(side="top", fill="both", padx=20, pady=20)

        info_label = tk.Label(info_frame, text="Información sobre los datos de precipitación:", font=("Arial", 14, "bold"))
        info_label.pack(fill="both", padx=10, pady=10)

        self.mostrar_pluvio_no_validos(info_frame)
        self.mostrar_saltos_temporales(info_frame)
        self.mostrar_porcentaje_nulos(info_frame)
        self.mostrar_acumulados_totales(info_frame)

    def mostrar_pluvio_no_validos(self, info_frame):
        tk.Label(info_frame, text="Pluviómetros no válidos", font=("Arial", 14, "bold")).pack(pady=10)
        pluvios_no_validos_label = tk.Label(info_frame, text=f"{', '.join(self.pluvio_no_validos)}", font=("Arial", 10), justify="left")
        pluvios_no_validos_label.pack(fill="both", padx=10, pady=15)

    def mostrar_saltos_temporales(self, info_frame):
        tk.Label(info_frame, text="Saltos temporales", font=("Arial", 10, "bold")).pack(pady=5)

        frame_tabla_saltos = tk.Frame(info_frame)
        frame_tabla_saltos.pack(fill="both", expand=True, pady=10)

        self.tabla = ttk.Treeview(frame_tabla_saltos, columns=("Pluviómetro", "Cantidad de saltos", "Duración total (min)", "Duración máx (min)", "Inicio máx", "Fin máx", "Grafica"), show="headings")
        self.tabla.heading("Pluviómetro", text="Pluviómetro")
        self.tabla.heading("Cantidad de saltos", text="Cantidad de saltos")
        self.tabla.heading("Duración total (min)", text="Duración total de saltos (min)")
        self.tabla.heading("Duración máx (min)", text="Duración salto mas largo (min)")
        self.tabla.heading("Inicio máx", text="Inicio")
        self.tabla.heading("Fin máx", text="Fin")
        self.tabla.heading("Grafica", text="Mostrar saltos en la grafica")

        self.tabla.column("Pluviómetro", width=150, anchor="center")
        self.tabla.column("Cantidad de saltos", width=100, anchor="center")
        self.tabla.column("Duración total (min)", width=150, anchor="center")
        self.tabla.column("Duración máx (min)", width=150, anchor="center")
        self.tabla.column("Inicio máx", width=150, anchor="center")
        self.tabla.column("Fin máx", width=150, anchor="center")
        self.tabla.column("Grafica", width=150, anchor="center")

        scrollbar = tk.Scrollbar(frame_tabla_saltos, orient="vertical", command=self.tabla.yview)
        scrollbar.pack(side="right", fill="y")
        self.tabla.configure(yscrollcommand=scrollbar.set)

        data = []
        if not self.df_saltos_maximos.empty:
            for index, row in self.df_saltos_maximos.iterrows():
                data.append((row["Pluviómetro"], row["Cantidad de saltos"], row["Duración total (min)"], row["Duración máx (min)"], row["Inicio máx"], row["Fin máx"], " ... "))
            
            data.sort(key=lambda x: x[2], reverse=True)
            for row in data:
                self.tabla.insert("", "end", values=row)
        else:
            self.tabla.insert("", "end", values=("No se detectaron saltos temporales", "", "", "", "", "",""))

        self.tabla.pack(fill="both", expand=True)
        self.tabla.bind("<Double-1>", self.mostrar_grafica_saltos)

    def mostrar_porcentaje_nulos(self, info_frame):
        tk.Label(info_frame, text="Porcentaje de nulos por pluviómetro", font=("Arial", 10, "bold")).pack()
        frame_tabla_porcentaje_nulos = tk.Frame(info_frame)
        frame_tabla_porcentaje_nulos.pack(fill="both", expand=True)

        tabla_nulos = ttk.Treeview(frame_tabla_porcentaje_nulos, columns=("Pluviómetro", "Porcentaje_Nulos"), show="headings")
        tabla_nulos.heading("Pluviómetro", text="Pluviómetro")
        tabla_nulos.heading("Porcentaje_Nulos", text="Porcentaje Nulos (%)")
        tabla_nulos.column("Pluviómetro", width=150, anchor="center")
        tabla_nulos.column("Porcentaje_Nulos", width=150, anchor="center")

        scrollbar_nulos = tk.Scrollbar(frame_tabla_porcentaje_nulos, orient="vertical", command=tabla_nulos.yview)
        scrollbar_nulos.pack(side="right", fill="y")
        tabla_nulos.configure(yscrollcommand=scrollbar_nulos.set)

        self.df_porcentaje_vacio = self.df_porcentaje_vacio.sort_values(by="Porcentaje_Nulos", ascending=False)
        for index, row in self.df_porcentaje_vacio.iterrows():
            tabla_nulos.insert("", "end", values=(row["Pluviómetro"], round(row["Porcentaje_Nulos"], 2)))

        tabla_nulos.pack(fill="both", expand=True, pady=5)

    def mostrar_acumulados_totales(self, info_frame):
        tk.Label(info_frame, text="Acumulados totales:", font=("Arial", 10, "bold")).pack(pady=5)
        frame_tabla_acumulado_total = tk.Frame(info_frame)
        frame_tabla_acumulado_total.pack(fill="both", expand=True)
        
        for col in self.df_acumulados_total.columns:
            label_columna = tk.Label(frame_tabla_acumulado_total, text=col, font=("Arial", 8, "bold"))
            label_columna.grid(row=0, column=self.df_acumulados_total.columns.get_loc(col), padx=5, pady=5)
            label_valor = tk.Label(frame_tabla_acumulado_total, text=self.df_acumulados_total[col].values[0], font=("Arial", 8))
            label_valor.grid(row=1, column=self.df_acumulados_total.columns.get_loc(col), padx=5, pady=5)
                
    def crear_botonera(self):
        botonera_frame = Frame(self)
        botonera_frame.pack(side="bottom", fill="y", padx=10, pady=10)
        
        volver_btn = tk.Button(botonera_frame, text="Volver", command=lambda: [self.cerrar_ventana(), VentanaLimiteTemporal(self.ventana_principal)], font=("Arial", 10, "bold"))
        volver_btn.pack(side="left", padx=10, pady=10)

        grafica_instantanea_btn = Button(botonera_frame, text="Ver Gráfico Lluvia Instantánea", 
                                         command=lambda: MostrarGrafica(graficar_lluvia_instantanea_tormenta(self.df_instantaneos)),
                                         font=("Arial", 10, "bold"))
        grafica_instantanea_btn.pack(side="left", padx=10, pady=10)

        grafica_acumulada_btn = Button(botonera_frame, text="Ver Gráfico Lluvia Acumulada", 
                                       command=lambda: MostrarGrafica(graficar_lluvia_acumulado_tormenta(self.df_acumulados)),
                                       font=("Arial", 10, "bold"))
        grafica_acumulada_btn.pack(side="left", padx=10, pady=10)
        
        grafica_tr_btn = Button(botonera_frame, text="Ver Gráfico Tr", 
                                       command=lambda: self.mostrar_interfaz_tr_tormenta(),
                                       font=("Arial", 10, "bold"))
        grafica_tr_btn.pack(side="left", padx=10, pady=10)

        procesar_btn = tk.Button(botonera_frame, text="Guardar Graficas", command=lambda: self.guardar_graficas(), font=("Arial", 10, "bold"))
        procesar_btn.pack(side="left", padx=10, pady=10)
    
    def cerrar_ventana(self):
        self.destroy()

class VentanaPrincipalMensual(tk.Toplevel):
    def __init__(self, ventana_principal):
        super().__init__()
        self.ventana_principal = ventana_principal
        
        self.df_datos = self.ventana_principal.df_datos
        self.df_acumulados = acumulados(self.df_datos)
        self.df_instantaneo = calcular_instantaneos(self.ventana_principal.df_datos)  
        self.df_acumulados_diarios = self.ventana_principal.df_acumulados_diarios      

        self.title("Ventana principal")
        self.state('zoomed')
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        self.crear_info_frame()
        self.crear_botonera()
    
    def crear_info_frame(self):
        info_frame = Frame(self)
        info_frame.pack(side="top", fill="both", padx=20, pady=20)

        info_label = tk.Label(info_frame, text="Información sobre los datos mensuales:", font=("Arial", 14, "bold"))
        info_label.pack(fill="both", padx=10, pady=10)
      
    def crear_botonera(self):
        botonera_frame = Frame(self)
        botonera_frame.pack(side="bottom", fill="y", padx=10, pady=10)
        
        tk.Button(botonera_frame, text="Reiniciar", command=self.regresar_inicio, font=("Arial", 10, "bold")).pack(side="left", pady=10, padx=10)
        
        graficar_acumulados_barras_btn = Button(botonera_frame, text="Ver Gráfico Acumulado Mensual", 
                                         command=lambda: MostrarGrafica(graficar_acumulados_barras(self.df_acumulados)),
                                         font=("Arial", 10, "bold"))
        graficar_acumulados_barras_btn.pack(side="left", padx=10, pady=10)
    
        graficar_acumulados_diarios_btn = Button(botonera_frame, text="Ver Gráfico Acumulado Diario", 
                                         command=lambda: MostrarGrafica(graficar_acumulados_diarios(self.df_acumulados_diarios)),
                                         font=("Arial", 10, "bold"))
        graficar_acumulados_diarios_btn.pack(side="left", padx=10, pady=10)
        
        grafica_lluvias_respecto_inumet_btn = Button(botonera_frame, text="Ver Gráfico Acumulado Respecto a INUMET", 
                                         command=lambda: MostrarGrafica(grafica_lluvias_respecto_inumet(self.df_acumulados_diarios)),
                                         font=("Arial", 10, "bold"))
        grafica_lluvias_respecto_inumet_btn.pack(side="left", padx=10, pady=10)
        
    def regresar_inicio(self):
        self.cerrar_ventana()
        self.ventana_principal.deiconify()
    
    def cerrar_ventana(self):
        self.destroy()
    
if __name__ == "__main__":
    app = VentanaInicio("", "")
