from tkinter import Frame
import tkinter as tk


class Prueba_checboxes:
    def __init__(self):
        
        self.pluvio_validos = ["Ciudad Vieja", "Punta Carretas"]
        
        self.principal = tk.Tk()
        self.principal.state('zoomed')
        self.principal.title("Ventana principal")
        
        self.inicializar_checkboxes()
        self.crear_checkboxes()
        
        self.principal.mainloop()
        
    def inicializar_checkboxes(self):
            self.checkboxes = {}
            # Crear IntVar para cada pluviómetro e inicializarlos en 1
            for pluvio in self.pluvio_validos:
                var = tk.IntVar(value=1)
                self.checkboxes[pluvio] = var  # Asociar el IntVar al pluviómetro
        
    def crear_checkboxes(self):
        check_frame = Frame(self.principal)
        check_frame.pack()

        row, col = 0, 0
        for pluvio in self.pluvio_validos:
            # Obtener el IntVar del diccionario (ya inicializado en 1)
            var = self.checkboxes[pluvio]

            # Crear Checkbutton con onvalue y offvalue explícitos
            checkbutton = tk.Checkbutton(
                check_frame, 
                text=pluvio, 
                variable=var, 
                font=("Arial", 10, "bold"), 
                onvalue=1, 
                offvalue=0,
                command=lambda pluvio=pluvio: self.imprimir_checkbox(pluvio)
            )
            checkbutton.grid(row=row, column=col, padx=10, pady=10, sticky="w")
            
            # Debugging: Ver si los valores iniciales son correctos
            print(f"{pluvio}: {var.get()}")
            
            # Organizar en columnas
            col += 1    
            if col > 6:
                col = 0
                row += 1

        
    def imprimir_checkbox(self, pluvio):

        var = self.checkboxes[pluvio]
        print(f"{pluvio}: {var.get()}")
                
if __name__ == "__main__":
    app = Prueba_checboxes()