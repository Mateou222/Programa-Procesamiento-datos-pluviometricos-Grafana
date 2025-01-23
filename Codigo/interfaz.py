from Funciones_basicas import *
from Funciones_tormenta import *
from Funciones_mensual import *


class Config(tk.Toplevel):
    def __init__(self, ventana_principal):
        super().__init__(ventana_principal)
        self.ventana_principal = ventana_principal
        
        self.df_datos = self.ventana_principal.df_datos
        self.df_config = self.ventana_principal.df_config
        self.ventana_principal.checkbox_config_bool = False        
        
        self.lugares_faltantes_id = detectar_id_faltante_config(self.df_config)
        
        self.title("Ventana configuraciones")
        self.geometry(self.centrar_ventana(500, 560))
        
        self.protocol("WM_DELETE_WINDOW", self.ventana_principal.cerrar_todo) 
        
        self.crear_interfaz()
    
    def centrar_ventana(self, ancho, alto):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        position_top = int(screen_height / 2 - alto / 2)
        position_left = int(screen_width / 2 - ancho / 2)
        return f'{ancho}x{alto}+{position_left}+{position_top}'
    
    def crear_interfaz(self):  
        self.crear_tabla()
        self.crear_botonera()
        
    def crear_tabla(self):  
        self.frame_config = tk.Frame(self)
        self.frame_config.pack(expand=True, fill="both", padx=10, pady=10)
        
        info_label = tk.Label(self.frame_config, text="Precionar ENTER despues de editar una celda", font=("Arial", 8))
        info_label.pack(fill="both", padx=10)
        
        # Añadir estilos para resaltar filas
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        
        # Crear un Treeview para mostrar los datos
        self.tabla_config = ttk.Treeview(
            self.frame_config, 
            columns=('Lugar', 'ID'), 
            show='headings', 
            height=16
        )
        self.tabla_config.heading('Lugar', text='Lugar')
        self.tabla_config.heading('ID', text='ID')

        # Insertar datos en el Treeview con color para los lugares sin ID
        for _, row in self.df_config.iterrows():
            lugar = row['Lugar']
            id_valor = row['ID'] if pd.notna(row['ID']) else ''  # Evitar mostrar NaN
            tag = 'sin_id' if lugar in self.lugares_faltantes_id else ''
            self.tabla_config.insert('', tk.END, values=(lugar, id_valor), tags=(tag,))

        # Configurar color para las filas con el tag 'sin_id'
        self.tabla_config.tag_configure('sin_id', background='#FFC0C0', foreground='black')

        # Habilitar la edición al hacer doble clic en una celda
        self.tabla_config.bind('<Double-1>', self.editar_celda)
        
        self.tabla_config.pack()

    def crear_botonera(self):
        # Crear un marco para centrar los botones horizontalmente
        self.botonera_frame = tk.Frame(self)
        self.botonera_frame.pack(side= "bottom", fill="x", expand=True)

        # Crear otro marco para los botones
        botones_frame = tk.Frame(self.botonera_frame)
        botones_frame.pack(side="top", fill="x")
        
        
                
        Guardar_btn = tk.Button(botones_frame, text="Guardar Configuraciones", command=lambda: self.guardar_config(), font=("Arial", 10, "bold"))
        Guardar_btn.pack(padx=10, pady=10)
        
        Volver_btn = tk.Button(botones_frame, text="Volver", command=lambda: self.volver_inicio(), font=("Arial", 10, "bold"))
        Volver_btn.pack( padx=10, pady=10)   
        
    def actualizar_df_config(self):
        """Actualizar el DataFrame con los datos del Treeview."""
        for i, item in enumerate(self.tabla_config.get_children()):
            values = self.tabla_config.item(item, 'values')
            lugar = values[0]
            id_valor = values[1]  # ID como cadena de texto
            self.df_config.at[i, 'Lugar'] = lugar
            self.df_config.at[i, 'ID'] = id_valor if id_valor.strip() != '' else None

    def editar_celda(self, event):
        """Editar una celda del Treeview."""
        # Obtener la celda seleccionada
        selected_item = self.tabla_config.selection()[0]
        column = self.tabla_config.identify_column(event.x)  # Columna seleccionada
        col_index = int(column[1:]) - 1  # Convertir columna "id" a índice 0/1
        old_value = self.tabla_config.item(selected_item, 'values')[col_index]

        # Crear un cuadro de entrada para editar la celda
        entry = tk.Entry(self.frame_config)
        entry.insert(0, old_value if old_value != "nan" else "")  # Evitar mostrar "nan"
        entry.select_range(0, tk.END)  # Seleccionar todo el texto
        entry.focus()

        # Posicionar el cuadro de entrada sobre la celda seleccionada
        bbox = self.tabla_config.bbox(selected_item, column)
        entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        
        # Manejar la actualización del valor al presionar Enter
        def guardar_edicion(event):
            new_value = entry.get()
            # Actualizar el Treeview
            current_values = list(self.tabla_config.item(selected_item, 'values'))
            current_values[col_index] = new_value
            self.tabla_config.item(selected_item, values=current_values)
            entry.destroy()  # Eliminar el cuadro de entrada
            # Actualizar el DataFrame
            self.actualizar_df_config()

        entry.bind('<Return>', guardar_edicion)
   
    def centrar_ventana(self, ancho, alto):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        position_top = int(screen_height / 2 - alto / 2)
        position_left = int(screen_width / 2 - ancho / 2)
        return f'{ancho}x{alto}+{position_left}+{position_top}'
    
    def guardar_config(self):
        if detectar_id_faltante_config(self.df_config):
            messagebox.showwarning("Advertencia", "Complete todos los IDs.")
        else:
            guardar_config(self.df_config)
            self.ventana_principal.df_datos = actualizar_columnas_datos_config(self.df_config, self.ventana_principal.df_datos)
            self.cerrar_ventana()
    
    def volver_inicio(self):
        self.destroy()
        self.ventana_principal.deiconify()
    
    def cerrar_ventana(self):
        self.destroy()
        self.ventana_principal.df_config = self.df_config
        self.siguiente()
    
    def siguiente(self):
        self.ventana_principal.df_datos_original = self.ventana_principal.df_datos
        if self.ventana_principal.analisis_seleccionado.get()== "Tormenta":
            return VentanaLimiteTemporal(self.ventana_principal)
        
        if self.ventana_principal.analisis_seleccionado.get()=="Mensual":
            df_instantaneo = calcular_instantaneos(self.df_datos)
            self.df_acumulados_diarios = calcular_acumulados_diarios(df_instantaneo)
            self.df_acumulados_diarios = leer_archivo_inumet(self.ventana_principal.archivo_inumet_seleccionado, self.df_acumulados_diarios)
                
            return VentanaPrincipalMensual(self.ventana_principal)        
    
class VentanaInicio(tk.Tk):
    def __init__(self):
        super().__init__()       
               
        self.title("Ventana de Inicio")
        self.geometry(self.centrar_ventana(500, 350))
        
        self.archivo_seleccionado = ""
        self.archivo_validador_seleccionado = ""
        self.archivo_inumet_seleccionado = ""
        
        self.archivo_principal_text = None
        self.archivo_validador_text = None
        self.archivo_inumet_text = None
        
        self.analisis_seleccionado = None
        
        self.comenzar_btn = None
        
        self.checkbox_config = tk.BooleanVar(value=False)
        self.checkbox_config_bool = False
        
        self.checkboxes = {}
        self.checkbox_inicio = True
                
        self.crear_interfaz()
        
        self.protocol("WM_DELETE_WINDOW", self.cerrar_todo) 
        
        self.mainloop()

    def centrar_ventana(self, ancho, alto):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        position_top = int(screen_height / 2 - alto / 2)
        position_left = int(screen_width / 2 - ancho / 2)
        return f'{ancho}x{alto}+{position_left}+{position_top}'

    def crear_interfaz(self):
        self.frame_archivo_principal()
        
        self.frame_seleccion_analisis()
        
        self.frame_archivo_inumet()

        self.frame_archivo_validador()
        
        self.frame_botonera()
   
        self.habilitar_boton_comenzar()

    def frame_archivo_principal(self):
        # Frame para seleccionar archivo principal
        archivo_frame = tk.Frame(self)
        archivo_frame.pack(pady=5)
        tk.Label(archivo_frame, text="Seleccionar archivo CSV: ", font=("Arial", 10, "bold")).pack(pady=5)
        
        self.archivo_principal_text = tk.Entry(archivo_frame, font=("Arial", 12), width=40)
        self.archivo_principal_text.pack(side=tk.LEFT, padx=5)
        
        if self.archivo_seleccionado:
            self.archivo_principal_text.insert(0, self.archivo_seleccionado)
        
        tk.Button(archivo_frame, text=" ... ", command=self.seleccionar_archivo_principal, font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        self.archivo_principal_text.bind("<FocusOut>", self.habilitar_boton_comenzar)

    def frame_seleccion_analisis(self):
        # Selección de tipo de análisis
        seleccion = tk.Frame(self)
        seleccion.pack(pady=5)
        tk.Label(seleccion, text="Seleccionar Tipo de análisis", font=("Arial", 10, "bold")).pack(pady=5)
        
        self.analisis_seleccionado = ttk.Combobox(seleccion, values=["Tormenta", "Mensual"])
        self.analisis_seleccionado.pack(pady=5)
        self.analisis_seleccionado.set("")
        
        self.analisis_seleccionado.bind("<<ComboboxSelected>>", self.habilitar_boton_comenzar)

    def frame_archivo_inumet(self):
        # Archivo INUMET
        archivo_inumet_frame = tk.Frame(self)
        archivo_inumet_frame.pack(pady=5)
        tk.Label(archivo_inumet_frame, text="Seleccionar archivo CSV de INUMET: ", font=("Arial", 10, "bold")).pack(pady=5)
        
        self.archivo_inumet_text = tk.Entry(archivo_inumet_frame, font=("Arial", 12), width=40)
        self.archivo_inumet_text.pack(side=tk.LEFT, padx=5)
        
        if self.archivo_inumet_text:
            self.archivo_inumet_text.insert(0, self.archivo_inumet_seleccionado)
        
        tk.Button(archivo_inumet_frame, text=" ... ", command=self.seleccionar_archivo_inumet, font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        self.archivo_inumet_text.bind("<FocusOut>", self.habilitar_boton_comenzar)

    def frame_archivo_validador(self):
        # Archivo validador
        archivo_validador_frame = tk.Frame(self)
        archivo_validador_frame.pack(pady=5)
        tk.Label(archivo_validador_frame, text="Seleccionar archivo CSV del validador: ", font=("Arial", 10, "bold")).pack(pady=5)
        
        self.archivo_validador_text = tk.Entry(archivo_validador_frame, font=("Arial", 12), width=40)
        self.archivo_validador_text.pack(side=tk.LEFT, padx=5)
        tk.Button(archivo_validador_frame, text=" ... ", command=self.seleccionar_archivo_verificador, font=("Arial", 10, "bold")).pack(side=tk.LEFT)

    def frame_botonera(self):
        # Crear un frame para centrar el checkbox y el botón
        opciones_frame = tk.Frame(self)
        opciones_frame.pack(pady=5)
        
        # Crear el checkbox configuraciones
        self.checkbox = tk.Checkbutton(opciones_frame, text="Configuraciones", variable=self.checkbox_config, command=lambda: self.actualizar_checkbox_config(), onvalue=True, offvalue=False, font=("Arial", 12))
        self.checkbox.pack(side= "left", pady=5)
        
        # Botón Siguiente
        self.comenzar_btn = tk.Button(opciones_frame, text="Siguiente", command=self.iniciar_ventanas, font=("Arial", 12, "bold"), state=tk.DISABLED)
        self.comenzar_btn.pack(side= "left", padx= 10, pady=5)

    def actualizar_checkbox_config(self):
        self.checkbox_config_bool = self.checkbox_config.get()   

    def seleccionar_archivo_principal(self):
        try:
            archivo = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
            if archivo:
                self.archivo_principal_text.delete(0, END)  # Borrar texto previo
                self.archivo_principal_text.insert(0, archivo)  # Rellenar con la ruta seleccionada
                self.archivo_seleccionado = archivo  # Guardar la ruta seleccionada en una variable global
                self.df_datos = leer_archivo_principal(self.archivo_seleccionado)
                self.habilitar_boton_comenzar()  # Habilitar el botón "Comenzar" si se ha seleccionado un archivo
        except:
            self.archivo_principal_text.delete(0, END)  # Borrar texto previo
            messagebox.showerror("Error","Seleccione un archivo valido de Grafana.\n\nRecuerde al descargar el archivo csv seleccionar en Opciones de datos:\nSeries unidades por el tiempo y no Descargar para Excel")

    def seleccionar_archivo_verificador(self):
        if self.archivo_principal_text.get():
            try:
                archivo = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
                if archivo:
                    self.archivo_validador_text.delete(0, END)  # Borrar texto previo
                    self.archivo_validador_text.insert(0, archivo)  # Rellenar con la ruta seleccionada
                    self.archivo_validador_seleccionado = archivo  # Guardar la ruta seleccionada en una variable global
                    self.df_datos = leer_archivo_verificador(self.archivo_validador_seleccionado, self.df_datos)
            except:
                self.archivo_validador_text.delete(0, END)
                messagebox.showerror("Error", "Error al abrir el archivo. Seleccione un archivo del validador.")
        else:
            messagebox.showinfo("Error", "Seleccione primero el archivo csv de Grafana.")
            
    def seleccionar_archivo_inumet(self):
        if self.archivo_principal_text.get():
            try:
                archivo = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
                if archivo:
                    self.archivo_inumet_text.delete(0, END)  # Borrar texto previo
                    self.archivo_inumet_text.insert(0, archivo)  # Rellenar con la ruta seleccionada
                    self.archivo_inumet_seleccionado = archivo  # Guardar la ruta seleccionada en una variable global
                    
                    df_instantaneo = calcular_instantaneos(self.df_datos)
                    df_acumulados_diarios = calcular_acumulados_diarios(df_instantaneo)
                    verificador = leer_archivo_inumet(self.archivo_inumet_seleccionado, df_acumulados_diarios)
                    
                    self.habilitar_boton_comenzar()
            except:
                    self.archivo_inumet_text.delete(0, END)
                    messagebox.showerror("Error", "Error al abrir el archivo. Seleccione un archivo de INUMET valido.\n\nRecuerde que el archivo csv de INUMET debe construirse de la siguiente forma:\n\n- Nombre columnas: FECHA | INUMET\n- Formato columnas: dd/mm/aaaa | valor precipitacion(mm)")
        else:
            messagebox.showinfo("Error", "Seleccione primero el archivo csv de Grafana.")

    def habilitar_boton_comenzar(self, event=None):
        if self.archivo_principal_text.get() and self.analisis_seleccionado.get() == "Tormenta":  # Si hay texto en el campo de archivo (es decir, si se ha seleccionado un archivo)
            self.comenzar_btn.config(state=NORMAL)  # Activar el botón "Comenzar"
        else:
            if self.analisis_seleccionado.get() == "Mensual" and self.archivo_principal_text.get() and self.archivo_inumet_text.get():
                self.comenzar_btn.config(state=NORMAL)  # Activar el botón "Comenzar
            else:
                self.comenzar_btn.config(state=DISABLED)  # De lo contrario, desactivar el botón "Comenzar"     
   
    def reiniciar_variables(self):
        self.archivo_principal_text.delete(0, END)
        self.analisis_seleccionado.set("")
        if self.archivo_inumet_text.get():
            self.archivo_inumet_text.delete(0, END)
        if self.archivo_validador_text.get():
            self.archivo_validador_text.delete(0, END)
            
        self.checkbox_config.set(False)
        self.actualizar_checkbox_config()
        
        self.habilitar_boton_comenzar()

    def iniciar_ventanas(self):
        self.checkbox_inicio = True
                                            
        self.df_config = cargar_config()
        self.df_config = agregar_equipos_nuevos_config(self.df_config, self.df_datos)
        self.df_config= eliminar_lugares_no_existentes_config(self.df_config, self.df_datos)
        
        if self.archivo_inumet_text.get():
            df_instantaneo = calcular_instantaneos(self.df_datos)
            self.df_acumulados_diarios = calcular_acumulados_diarios(df_instantaneo)
            self.df_acumulados_diarios = leer_archivo_inumet(self.archivo_inumet_seleccionado, self.df_acumulados_diarios)
        
        if detectar_id_faltante_config(self.df_config) or self.checkbox_config_bool:
            self.checkbox_config.set(False)
            self.actualizar_checkbox_config()
            self.cerrar_ventana()
            Config(self)
        else:
            self.df_datos = actualizar_columnas_datos_config(self.df_config, self.df_datos)
            self.df_datos_original = self.df_datos
            
            
            if self.analisis_seleccionado.get()== "Tormenta":
                self.cerrar_ventana()
                return VentanaLimiteTemporal(self)
            
            if self.analisis_seleccionado.get()=="Mensual":             
                self.cerrar_ventana()
                return VentanaPrincipalMensual(self)
     
    def cerrar_todo(self):
        self.quit()  # Termina el mainloop de Tkinter
        self.destroy()
    
    def cerrar_ventana(self):
        self.withdraw()

class VentanaLimiteTemporal(tk.Toplevel):
    def __init__(self, ventana_principal):
        super().__init__(ventana_principal)
        self.ventana_principal = ventana_principal
        
        self.df_datos = self.ventana_principal.df_datos
        self.df_datos_original = self.ventana_principal.df_datos_original
        
        pluvio_validos, pluvio_no_validos = obtener_pluviometros_validos(self.df_datos)
        df_lluvia_instantanea = calcular_instantaneos(self.df_datos_original)

        self.lluvia_filtrada = df_lluvia_instantanea[pluvio_validos]
        
        self.title("Ventana limite temporal")
        self.state('zoomed')
        
        self.limite_inf_selector = None
        self.limite_sup_selector = None
        self.frame_grafica = None
                
        self.crear_interfaz()
        self.actualizar_grafica()
        
        self.protocol("WM_DELETE_WINDOW", self.ventana_principal.cerrar_todo) 
        
    def crear_interfaz(self):
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
        self.ventana_principal.reiniciar_variables()
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

class PluviometrosSeleccionados(Frame):
    def __init__(self,ventana_principal, ventana_actual ,parent, pluvio_validos, checkboxes):
        super().__init__(parent)
        self.ventana_actual = ventana_actual
        self.ventana_principal = ventana_principal
        
        self.pluvio_validos = pluvio_validos
        self.checkboxes = checkboxes
        self.df_config = self.ventana_principal.df_config
        self.checkbox_inicio = self.ventana_principal.checkbox_inicio

        if self.checkbox_inicio:
            self.inicializar_checkboxes()
            self.ventana_principal.checkbox_inicio = False
        self.crear_checkboxes()
    
    def inicializar_checkboxes(self):
        # Crear IntVar para cada pluviómetro e inicializarlos en 1
        for pluvio in self.pluvio_validos:
            var = IntVar(value=1)
            self.checkboxes[pluvio] = var
    
    def crear_checkboxes(self):
        row, col = 0, 0
        for pluvio in self.pluvio_validos:
            # Obtener el IntVar del diccionario
            var = self.checkboxes[pluvio]

            # Crear Checkbutton con onvalue y offvalue explícitos
            checkbutton = Checkbutton(
                self,  # El contenedor es el Frame actual
                text=traducir_id_a_lugar(self.df_config, pluvio),
                variable=var,
                font=("Arial", 10, "bold"),
                onvalue=1,
                offvalue=0,
                command=lambda pluvio=pluvio: self.actualizar_checkbox()
            )
            checkbutton.grid(row=row, column=col, padx=10, pady=10, sticky="w")
            
            # Organizar en columnas
            col += 1
            if col > 6:
                col = 0
                row += 1

    def actualizar_checkbox(self):
        self.ventana_principal.checkboxes = self.checkboxes
        self.ventana_actual.actualizar_acumulado_total()
    
class VentanaPrincipalTormenta(tk.Toplevel):
    def __init__(self, ventana_principal):
        super().__init__(ventana_principal)
        self.ventana_principal = ventana_principal
        
        self.checkbox_inicio = self.ventana_principal.checkbox_inicio
        
        self.title("Ventana principal")
        self.state('zoomed')
        
        self.df_config = self.ventana_principal.df_config
        self.df_datos = self.ventana_principal.df_datos
        self.pluvio_validos, self.pluvio_no_validos = obtener_pluviometros_validos(self.df_datos)
        self.df_acumulados = acumulados(self.df_datos)
        self.df_instantaneos = calcular_instantaneos(self.df_datos)
        self.df_saltos_maximos, self.df_saltos = detectar_saltos_temporales(self.df_datos[self.pluvio_validos], self.df_config)
        self.df_porcentaje_vacio = calcular_porcentaje_vacios(self.df_datos[self.pluvio_validos], self.df_config)

        self.checkboxes = self.ventana_principal.checkboxes
        
        self.protocol("WM_DELETE_WINDOW", self.ventana_principal.cerrar_todo) 
        
        self.crear_interfaz()

    def filtrar_pluvios_seleccionados(self, df):
        # Obtener los pluviómetros seleccionados (los que tienen valor 1 en self.checkboxes)
        pluvios_seleccionados = [pluvio for pluvio, var in self.ventana_principal.checkboxes.items() if var.get() == 1]
        
        # Filtrar las columnas del dataframe self.df_instantaneos para solo mantener las seleccionadas
        df_seleccionados = df[pluvios_seleccionados]
        
        return df_seleccionados 

    def crear_interfaz(self):
        self.crear_info_frame()
        self.crear_checkboxes()
        self.crear_botonera()
    
    def crear_info_frame(self):
        self.info_frame = Frame(self)
        self.info_frame.pack(side="top", fill="both", padx=20, pady=20)

        info_label = tk.Label(self.info_frame, text="Información sobre los datos de precipitación:", font=("Arial", 14, "bold"))
        info_label.pack(fill="both", padx=10, pady=10)

        self.mostrar_pluvio_no_validos()
        self.mostrar_saltos_temporales()
        self.mostrar_porcentaje_nulos()
        self.mostrar_acumulados_totales()
        
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

    def mostrar_pluvio_no_validos(self):
        tk.Label(self.info_frame, text="Pluviómetros no válidos", font=("Arial", 14, "bold")).pack(pady=10)
        # Convertir cada ID en 'pluvio_no_validos' a su nombre de lugar
        lugares_no_validos = [traducir_id_a_lugar(self.df_config, id_pluvio) for id_pluvio in self.pluvio_no_validos]
        # Crear una cadena de texto con los lugares no válidos, separada por comas
        lugares_no_validos = ", ".join(lugares_no_validos)
        pluvios_no_validos_label = tk.Label(self.info_frame, text=lugares_no_validos, font=("Arial", 10), justify="left")
        pluvios_no_validos_label.pack(fill="both", padx=10, pady=15)

    def mostrar_saltos_temporales(self):
        tk.Label(self.info_frame, text="Saltos temporales", font=("Arial", 10, "bold")).pack(pady=5)

        frame_tabla_saltos = tk.Frame(self.info_frame)
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

    def mostrar_porcentaje_nulos(self):
        tk.Label(self.info_frame, text="Porcentaje de nulos por pluviómetro", font=("Arial", 10, "bold")).pack()
        frame_tabla_porcentaje_nulos = tk.Frame(self.info_frame)
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

    def mostrar_acumulados_totales(self):
        tk.Label(self.info_frame, text="Acumulados totales:", font=("Arial", 10, "bold")).pack(pady=5)

        # Crear un Frame para contener tanto el Treeview como el botón
        frame_contenedor = tk.Frame(self.info_frame)
        frame_contenedor.pack(fill="both", expand=True)

        # Crear un Frame para el botón
        frame_boton = tk.Frame(frame_contenedor)
        frame_boton.pack(side="left")

        # Crear un botón en el frame_boton
        copiar_btn = tk.Button(frame_boton, text="Copiar", command=self.copiar_tabla_acumulado_al_portapapeles)
        copiar_btn.pack(side="left")
        
        # Crear un Frame para la tabla (Treeview)
        frame_tabla_acumulado_total = tk.Frame(frame_contenedor)
        frame_tabla_acumulado_total.pack(side="right", fill="both", expand=True, padx=10)
        
        # Crear un Treeview con columnas dinámicas
        self.tabla_acumulado_total = ttk.Treeview(frame_tabla_acumulado_total, show="headings", height=1)
        
        if self.checkbox_inicio:
            df_acumulados_filtrado = self.df_acumulados[self.pluvio_validos]
        else:   
            # Agregar columnas
            df_acumulados_filtrado = self.filtrar_pluvios_seleccionados(self.df_acumulados)
        
        self.df_acumulados_total = acumulado_total(df_acumulados_filtrado)
        self.df_acumulados_total = self.df_acumulados_total.round(1)
        
        self.tabla_acumulado_total["columns"] = self.df_acumulados_total.columns.tolist()
        
        # Configurar los encabezados de las columnas
        for col in self.df_acumulados_total.columns:
            self.tabla_acumulado_total.heading(col, text=col)
            self.tabla_acumulado_total.column(col, width=50, anchor="center")  # Ajustar ancho y alineación

        # Insertar los datos
        for i, row in self.df_acumulados_total.iterrows():
            self.tabla_acumulado_total.insert("", "end", values=row.tolist())

        # Crear un Scrollbar horizontal
        scrollbar = tk.Scrollbar(frame_tabla_acumulado_total, orient="horizontal", command=self.tabla_acumulado_total.xview)
        self.tabla_acumulado_total.config(xscrollcommand=scrollbar.set)
        scrollbar.pack(side="bottom", fill="x")

        # Crear un Scrollbar vertical (opcional, si hay muchas filas)
        scrollbar_vertical = tk.Scrollbar(frame_tabla_acumulado_total, orient="vertical", command=self.tabla_acumulado_total.yview)
        self.tabla_acumulado_total.config(yscrollcommand=scrollbar_vertical.set)
        scrollbar_vertical.pack(side="right", fill="y")

        # Empaquetar el Treeview
        self.tabla_acumulado_total.pack(fill="both", expand=True)

    def actualizar_acumulado_total(self):
        # Elimina todos los elementos existentes
        for item in self.tabla_acumulado_total.get_children():
            self.tabla_acumulado_total.delete(item)
        df_acumulados_filtrado = self.filtrar_pluvios_seleccionados(self.df_acumulados)
        
        self.df_acumulados_total = acumulado_total(df_acumulados_filtrado)
        self.df_acumulados_total = self.df_acumulados_total.round(1)
        
        self.tabla_acumulado_total["columns"] = self.df_acumulados_total.columns.tolist()
        
        # Configurar los encabezados de las columnas
        for col in self.df_acumulados_total.columns:
            self.tabla_acumulado_total.heading(col, text=col)
            self.tabla_acumulado_total.column(col, width=50, anchor="center")  # Ajustar ancho y alineación

        # Insertar los datos
        for i, row in self.df_acumulados_total.iterrows():
            self.tabla_acumulado_total.insert("", "end", values=row.tolist())
         
    
    def copiar_tabla_acumulado_al_portapapeles(self):
        # Extraer los datos de la tabla (celdas) y convertirlo en un formato adecuado para copiar
        table_data = []

        # Agregar encabezados de columna
        headers = self.df_acumulados_total.columns.tolist()
        table_data.append("\t".join(headers))
        
        # Agregar filas de datos
        for row_id in self.tabla_acumulado_total.get_children():
            row_values = self.tabla_acumulado_total.item(row_id)["values"]
            table_data.append("\t".join(map(str, row_values)))
        
        # Convertir la lista de filas en un string con saltos de línea
        table_str = "\n".join(table_data)
        
        # Copiar el texto al portapapeles usando pyperclip
        pyperclip.copy(table_str)
            
    def crear_checkboxes(self):
        frame_checkboxes = tk.Frame(self)
        frame_checkboxes.pack(fill="both", expand=True)
        
        frame_pluvios = PluviometrosSeleccionados(self.ventana_principal, self, frame_checkboxes, self.pluvio_validos, self.checkboxes)
        frame_pluvios.pack()
     
    def crear_botonera(self):
        botonera_frame = Frame(self)
        botonera_frame.pack(side="bottom", fill="y", padx=10, pady=10)
        
        volver_btn = tk.Button(botonera_frame, text="Volver", command=lambda: [self.cerrar_ventana(), VentanaLimiteTemporal(self.ventana_principal)], font=("Arial", 10, "bold"))
        volver_btn.pack(side="left", padx=10, pady=10)

        grafica_instantanea_btn = Button(botonera_frame, text="Ver Gráfico Lluvia Instantánea", 
                                         command=lambda: MostrarGrafica(graficar_lluvia_instantanea_tormenta(self.filtrar_pluvios_seleccionados(self.df_instantaneos))),
                                         font=("Arial", 10, "bold"))
        grafica_instantanea_btn.pack(side="left", padx=10, pady=10)

        grafica_acumulada_btn = Button(botonera_frame, text="Ver Gráfico Lluvia Acumulada", 
                                       command=lambda: MostrarGrafica(graficar_lluvia_acumulado_tormenta((self.filtrar_pluvios_seleccionados(self.df_acumulados)))),
                                       font=("Arial", 10, "bold"))
        grafica_acumulada_btn.pack(side="left", padx=10, pady=10)
        
        grafica_tr_btn = Button(botonera_frame, text="Ver Gráfico Tr", 
                                       command=lambda: self.mostrar_interfaz_tr_tormenta(),
                                       font=("Arial", 10, "bold"))
        grafica_tr_btn.pack(side="left", padx=10, pady=10)

        Guardar_btn = tk.Button(botonera_frame, text="Guardar Graficas", command=lambda: self.guardar_graficas(), font=("Arial", 10, "bold"))
        Guardar_btn.pack(side="left", padx=10, pady=10)
    
    def mostrar_interfaz_tr_tormenta(self):    
        lluvia_filtrada = self.filtrar_pluvios_seleccionados(self.df_instantaneos)
        
        if lluvia_filtrada.empty:
            messagebox.showwarning("Advertencia", "Seleccione al menos un pluviómetro.")
            return
        
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
        
        def actualizar_limites():
            if ultima_grafica == "pluviómetro":
                graficar_pluv()
            else:
                graficar_todos()
        
        
        # Checkboxes para TRs
        lista_tr = [tk.IntVar(value=v) for v in [1, 1, 1, 1, 0, 1, 0]]
        tr_labels = ["TR 2 años", "TR 5 años", "TR 10 años", "TR 20 años", "TR 25 años", "TR 50 años", "TR 100 años"]
        tk.Label(frame_izq, text="Seleccionar TRs", font="bold").pack(pady=10, padx=10)
        for i, tr in enumerate(tr_labels):
            tk.Checkbutton(frame_izq, text=tr, variable=lista_tr[i], command=actualizar_limites).pack(anchor="w")
            
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
    
    def guardar_graficas(self):       
        
        # Aquí puedes llamar a la función que procesa los pluviómetros seleccionados
        # por ejemplo: guardar las graficas y esas manos
        #lluvia_filtrada_inst = self.df_instantaneos[self.seleccionados]
        lluvia_filtrada_inst = self.filtrar_pluvios_seleccionados(self.df_instantaneos)
        
        if lluvia_filtrada_inst.empty:
            messagebox.showwarning("Advertencia", "Seleccione al menos un pluviómetro.")
            return
        
        # Cuadro de diálogo para seleccionar directorio y nombre del archivo
        directorio = filedialog.askdirectory(title="Selecciona un directorio para guardar las gráficas")
            
        fig_inst = graficar_lluvia_instantanea_tormenta(lluvia_filtrada_inst)
        fig_inst.savefig(f"{directorio}/grafica instantaneas.png")
        
        #lluvia_filtrada_acum = self.lluvia_acumulada[self.seleccionados]
        lluvia_filtrada_acum = self.filtrar_pluvios_seleccionados(self.df_acumulados)
        
        fig_acum = graficar_lluvia_acumulado_tormenta(lluvia_filtrada_acum)
        # Guardar la primera gráfica
        fig_acum.savefig(f"{directorio}/grafica acumulado.png")
        
        messagebox.showinfo("Exito", "Procesado correctamente.")    

    def cerrar_ventana(self):
        self.destroy()

class VentanaPrincipalMensual(tk.Toplevel):
    def __init__(self, ventana_principal):
        super().__init__(ventana_principal)
        self.ventana_principal = ventana_principal
        
        self.df_datos = self.ventana_principal.df_datos
        self.checkbox_inicio = self.ventana_principal.checkbox_inicio
        self.df_config = self.ventana_principal.df_config
        
        self.df_instantaneo = calcular_instantaneos(self.df_datos)  
        self.pluvio_validos, self.pluvio_no_validos = obtener_pluviometros_validos(self.df_datos)
        
        self.df_acumulados = acumulados(self.df_datos)
        self.df_acumulados_diarios = self.ventana_principal.df_acumulados_diarios      
        self.df_correlacion = tabla_correlacion(self.df_acumulados_diarios)

        self.checkboxes = self.ventana_principal.checkboxes

        self.title("Ventana principal")
        self.state('zoomed')
        
        self.protocol("WM_DELETE_WINDOW", self.ventana_principal.cerrar_todo) 
        
        self.crear_interfaz()

    def filtrar_pluvios_seleccionados(self, df):
        # Obtener los pluviómetros seleccionados (los que tienen valor 1 en self.checkboxes)
        pluvios_seleccionados = [pluvio for pluvio, var in self.ventana_principal.checkboxes.items() if var.get() == 1]
        
        # Asegurar que INUMET siempre esté incluido
        pluvios_seleccionados.append("INUMET")
        
        # Filtrar las columnas del dataframe self.df_instantaneos para solo mantener las seleccionadas
        df_seleccionados = df[pluvios_seleccionados]
        
        return df_seleccionados

    def crear_interfaz(self):
        self.crear_info_frame()
        self.crear_checkboxes()
        self.crear_botonera()
    
    def crear_info_frame(self):
        self.info_frame = Frame(self)
        self.info_frame.pack(side="top", fill="both", padx=20, pady=20)

        info_label = tk.Label(self.info_frame, text="Información sobre los datos mensuales:", font=("Arial", 14, "bold"))
        info_label.pack(fill="both", padx=10, pady=10)
        
        self.mostrar_tabla_correlacion()
        
        self.mostrar_acumulados_totales()
        
        self.mostrar_tabla_percentiles()
    
    def mostrar_tabla_correlacion(self):
        
        tk.Label(self.info_frame, text="Tabla correlacion:", font=("Arial", 10, "bold")).pack(pady=5)
        
        # Crear un Frame para contener tanto el Treeview como el botón
        frame_contenedor = tk.Frame(self.info_frame)
        frame_contenedor.pack(fill="both", expand=True)
        
        # Crear un Frame para el botón
        frame_boton = tk.Frame(frame_contenedor)
        frame_boton.pack(side="left", padx=10)
        
        # Crear un botón en el frame_boton
        copiar_btn = tk.Button(frame_boton, text="Copiar", command=self.copiar_tabla_al_portapapeles_correlacion)
        copiar_btn.pack(side="left")
        
        # Crear un Frame para la tabla (Treeview)
        frame_tabla_correlacion = tk.Frame(frame_contenedor)
        frame_tabla_correlacion.pack(side="right", fill="both", expand=True, pady=10)

        # Crear el widget Treeview con una columna extra para los índices de las filas
        self.tree = ttk.Treeview(frame_tabla_correlacion, show="headings")
        
        # Crear las columnas del Treeview, incluyendo una para los índices
        self.tree["columns"] = ["index"] + list(self.df_correlacion.columns)
        
        # Configurar la primera columna para los índices de las filas
        self.tree.heading("index", text="Índices")
        self.tree.column("index", anchor="center", width=50)  # Puedes ajustar el ancho
        
        # Configurar las otras columnas para las variables, ajustando el ancho
        for col in self.df_correlacion.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=50)  # Ajusta el ancho a 100 o lo que consideres adecuado

        # Insertar las filas de datos, incluyendo los índices de las filas en la primera columna
        for idx, row in self.df_correlacion.iterrows():
            self.tree.insert("", "end", values=[idx] + list(row))
        
        # Crear un Scrollbar para la tabla
        scrollbar = tk.Scrollbar(frame_tabla_correlacion, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Mostrar el Treeview en la interfaz
        self.tree.pack(fill="both", expand=True) 
            
    def copiar_tabla_al_portapapeles_correlacion(self):
        # Extraer los datos de la tabla (celdas) y convertirlo en un formato adecuado para Excel
        table_data = []
        
        # Agregar encabezados de columna
        headers = ["Índices"] + list(self.df_correlacion.columns)
        table_data.append("\t".join(headers))
        
        # Agregar filas de datos
        for idx, row in self.df_correlacion.iterrows():
            row_values = [str(idx)] + list(map(str, row))
            table_data.append("\t".join(row_values))
        
        # Convertir la lista de filas en un string con saltos de línea
        table_str = "\n".join(table_data)
        
        # Copiar el texto al portapapeles usando pyperclip
        pyperclip.copy(table_str)

    def mostrar_acumulados_totales(self):
        tk.Label(self.info_frame, text="Acumulados totales:", font=("Arial", 10, "bold")).pack(pady=5)

        # Crear un Frame para contener tanto el Treeview como el botón
        frame_contenedor = tk.Frame(self.info_frame)
        frame_contenedor.pack(fill="both", expand=True)

        # Crear un Frame para el botón
        frame_boton = tk.Frame(frame_contenedor)
        frame_boton.pack(side="left")

        # Crear un botón en el frame_boton
        copiar_btn = tk.Button(frame_boton, text="Copiar", command=self.copiar_tabla_al_portapapeles_acumulado_total)
        copiar_btn.pack(side="left")
        
        # Crear un Frame para la tabla (Treeview)
        frame_tabla_acumulado_total = tk.Frame(frame_contenedor)
        frame_tabla_acumulado_total.pack(side="right", fill="both", expand=True, padx= 10)


        # Crear un Treeview con columnas dinámicas
        self.tabla_acumulado_total = ttk.Treeview(frame_tabla_acumulado_total, show="headings", height=1)
        
        df_acumulados_diarios_traducido = traducir_columnas_lugar_a_id(self.df_config, self.df_acumulados_diarios)
        
        if self.checkbox_inicio:
            pluv_validos = self.pluvio_validos.copy()
            pluv_validos.append("INUMET")
            df_acumulados_filtrado = df_acumulados_diarios_traducido[pluv_validos]
        else:   
            # Agregar columnas
            df_acumulados_filtrado = self.filtrar_pluvios_seleccionados(df_acumulados_diarios_traducido)
            
        df_acumulados_total = acumulado_diarios_total(df_acumulados_filtrado)
        df_acumulados_total = acumulado_total(df_acumulados_total)
            
        
        df_acumulados_total = df_acumulados_total.round(1)
        
        self.tabla_acumulado_total["columns"] = df_acumulados_total.columns.tolist()
        
        # Configurar los encabezados de las columnas
        for col in df_acumulados_total.columns:
            self.tabla_acumulado_total.heading(col, text=col)
            self.tabla_acumulado_total.column(col, width=50, anchor="center")  # Ajustar ancho y alineación

        # Insertar los datos
        for i, row in df_acumulados_total.iterrows():
            self.tabla_acumulado_total.insert("", "end", values=row.tolist())

        # Crear un Scrollbar horizontal
        scrollbar = tk.Scrollbar(frame_tabla_acumulado_total, orient="horizontal", command=self.tabla_acumulado_total.xview)
        self.tabla_acumulado_total.config(xscrollcommand=scrollbar.set)
        scrollbar.pack(side="bottom", fill="x")

        # Crear un Scrollbar vertical (opcional, si hay muchas filas)
        scrollbar_vertical = tk.Scrollbar(frame_tabla_acumulado_total, orient="vertical", command=self.tabla_acumulado_total.yview)
        self.tabla_acumulado_total.config(yscrollcommand=scrollbar_vertical.set)
        scrollbar_vertical.pack(side="right", fill="y")

        # Empaquetar el Treeview
        self.tabla_acumulado_total.pack(fill="both", expand=True)

    def actualizar_acumulado_total(self):
        # Elimina todos los elementos existentes
        for item in self.tabla_acumulado_total.get_children():
            self.tabla_acumulado_total.delete(item)
            
        df_acumulados_diarios_traducido = traducir_columnas_lugar_a_id(self.df_config, self.df_acumulados_diarios)
        df_acumulados_filtrado = self.filtrar_pluvios_seleccionados(df_acumulados_diarios_traducido)

        df_acumulados_total = acumulado_diarios_total(df_acumulados_filtrado)

        df_acumulados_total = acumulado_total(df_acumulados_total)
        df_acumulados_total = df_acumulados_total.round(1)
        
        self.tabla_acumulado_total["columns"] = df_acumulados_total.columns.tolist()
        
        # Configurar los encabezados de las columnas
        for col in df_acumulados_total.columns:
            self.tabla_acumulado_total.heading(col, text=col)
            self.tabla_acumulado_total.column(col, width=50, anchor="center")  # Ajustar ancho y alineación

        # Insertar los datos
        for i, row in df_acumulados_total.iterrows():
            self.tabla_acumulado_total.insert("", "end", values=row.tolist())

    def copiar_tabla_al_portapapeles_acumulado_total(self):
        # Extraer los datos de la tabla (celdas) y convertirlo en un formato adecuado para copiar
        table_data = []

        # Agregar encabezados de columna
        headers = self.df_acumulados_total.columns.tolist()
        table_data.append("\t".join(headers))
        
        # Agregar filas de datos
        for row_id in self.tabla_acumulado_total.get_children():
            row_values = self.tabla_acumulado_total.item(row_id)["values"]
            table_data.append("\t".join(map(str, row_values)))
        
        # Convertir la lista de filas en un string con saltos de línea
        table_str = "\n".join(table_data)
        
        # Copiar el texto al portapapeles usando pyperclip
        pyperclip.copy(table_str)

    def mostrar_tabla_percentiles(self):
        mes = obtener_mes(self.df_acumulados_diarios)
        mes_str = numero_a_mes(mes)
        lista_percentil = valor_lluvias_historicas(mes)
        
        tk.Label(self.info_frame, text=f"Tabla cuantiles precipitacion del mes de {mes_str}:", font=("Arial", 10, "bold")).pack(pady=5)

        # Crear un Frame para contener tanto el Treeview como el botón
        frame_contenedor = tk.Frame(self.info_frame)
        frame_contenedor.pack(fill="both", expand=True)

        # Crear un Frame para el botón
        frame_boton = tk.Frame(frame_contenedor)
        frame_boton.pack(side="left")

        # Crear un botón en el frame_boton
        copiar_btn = tk.Button(frame_boton, text="Copiar", command=self.copiar_tabla_al_portapapeles_percentil)
        copiar_btn.pack(side="left")
        
        # Crear un Frame para la tabla (Treeview)
        frame_tabla_percentil = tk.Frame(frame_contenedor)
        frame_tabla_percentil.pack(side="right", fill="both", expand=True, padx=10)
        
        # Crear un Treeview con columnas dinámicas
        self.tabla_percentiles = ttk.Treeview(frame_tabla_percentil, show="headings", height=1)
        
        self.nombre_percentil = ["Primer cuartil", "Mediana", "Tercer cuartil", "Maximo"]
        self.tabla_percentiles["columns"] = self.nombre_percentil
        
        # Configurar los encabezados de las columnas
        for col in self.nombre_percentil:
            self.tabla_percentiles.heading(col, text=col)
            self.tabla_percentiles.column(col, width=100, anchor="center") 

        self.tabla_percentiles.insert("", "end", values=lista_percentil)

        # Empaquetar el Treeview
        self.tabla_percentiles.pack(fill="both", expand=True)
                 
    def copiar_tabla_al_portapapeles_percentil(self):
        # Extraer los encabezados de las columnas
        headers = [self.tabla_percentiles.heading(col)["text"] for col in self.tabla_percentiles["columns"]]
        table_data = ["\t".join(headers)]  # Crear la primera fila con los encabezados

        # Extraer los datos de las filas
        for row in self.tabla_percentiles.get_children():
            values = self.tabla_percentiles.item(row)["values"]
            table_data.append("\t".join(map(str, values)))

        # Unir todas las filas con saltos de línea
        table_str = "\n".join(table_data)

        # Copiar al portapapeles
        try:
            pyperclip.copy(table_str)
        except Exception as e:
            tk.messagebox.showerror("Error", f"No se pudo copiar al portapapeles: {e}")
    
    def crear_checkboxes(self):
            frame_checkboxes = tk.Frame(self)
            frame_checkboxes.pack(fill="both", expand=True)
            
            frame_pluvios = PluviometrosSeleccionados(self.ventana_principal,self, frame_checkboxes, self.pluvio_validos, self.checkboxes)
            frame_pluvios.pack()    

    def crear_botonera(self):
        botonera_frame = Frame(self)
        botonera_frame.pack(side="bottom", fill="y", padx=10, pady=10)
        
        tk.Button(botonera_frame, text="Reiniciar", command=self.regresar_inicio, font=("Arial", 10, "bold")).pack(side="left", pady=10, padx=10)
        
        graficar_acumulados_barras_btn = Button(botonera_frame, text="Ver Gráfico Acumulado Mensual", 
                                         command=lambda: MostrarGrafica(graficar_acumulados_barras((self.filtrar_pluvios_seleccionados(self.df_acumulados_diarios)))),
                                         font=("Arial", 10, "bold"))
        graficar_acumulados_barras_btn.pack(side="left", padx=10, pady=10)
    
        graficar_acumulados_diarios_btn = Button(botonera_frame, text="Ver Gráfico Acumulado Diario", 
                                         command=lambda: MostrarGrafica(graficar_acumulados_diarios((self.filtrar_pluvios_seleccionados(self.df_acumulados_diarios)))),
                                         font=("Arial", 10, "bold"))
        graficar_acumulados_diarios_btn.pack(side="left", padx=10, pady=10)
        
        grafica_lluvias_respecto_inumet_btn = Button(botonera_frame, text="Ver Gráfico Acumulado Respecto a INUMET", 
                                         command=lambda: MostrarGrafica(grafica_lluvias_respecto_inumet(self.df_acumulados_diarios)), font=("Arial", 10, "bold"))
        grafica_lluvias_respecto_inumet_btn.pack(side="left", padx=10, pady=10)
        
        Guardar_btn = tk.Button(botonera_frame, text="Guardar Graficas", command=lambda: self.guardar_graficas(), font=("Arial", 10, "bold"))
        Guardar_btn.pack(side="left", padx=10, pady=10)

    # Función que se ejecuta cuando el usuario da click en "Procesar"
    def guardar_graficas(self):       
        
        # Aquí puedes llamar a la función que procesa los pluviómetros seleccionados
        # por ejemplo: guardar las graficas y esas manos
        #lluvia_filtrada_inst = self.df_instantaneos[self.seleccionados]
        lluvia_filtrada_barras = self.filtrar_pluvios_seleccionados(self.df_acumulados_diarios)
        
        if lluvia_filtrada_barras.empty:
            messagebox.showwarning("Advertencia", "Seleccione al menos un pluviómetro.")
            return
        
        # Cuadro de diálogo para seleccionar directorio y nombre del archivo
        directorio = filedialog.askdirectory(title="Selecciona un directorio para guardar las gráficas")
            
        fig_barras = graficar_acumulados_barras(lluvia_filtrada_barras)
        fig_barras.savefig(f"{directorio}/grafica acumulado mensual.png")
        
        #lluvia_filtrada_acum = self.lluvia_acumulada[self.seleccionados]
        lluvia_filtrada_acum_diario = self.filtrar_pluvios_seleccionados(self.df_acumulados_diarios)
        
        fig_acum = graficar_acumulados_diarios(lluvia_filtrada_acum_diario)
        # Guardar la primera gráfica
        fig_acum.savefig(f"{directorio}/grafica acumulado diario.png")
        
        fig_inumet= grafica_lluvias_respecto_inumet(self.df_acumulados_diarios)
        # Guardar la primera gráfica
        fig_inumet.savefig(f"{directorio}/grafica acumulado respecto INUMET.png")
        
        messagebox.showinfo("Exito", "Procesado correctamente.")
  
    def regresar_inicio(self):
        self.cerrar_ventana()
        self.ventana_principal.reiniciar_variables()
        self.ventana_principal.deiconify()
    
    def cerrar_ventana(self):
        self.destroy()

    
