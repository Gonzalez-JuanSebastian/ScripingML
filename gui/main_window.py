import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk  # Asegúrate de tener Pillow instalado
import os

class MainWindow:
    def __init__(self, root, main_process):
        self.root = root
        self.main_process = main_process

        self.create_widgets()

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Cargar y mostrar el logo
        try:
            # Ruta al logo dentro de la carpeta img
            logo_path = os.path.join(os.path.dirname(__file__), 'img', 'Logo ABIN S A S EDITADO.png')
            logo = Image.open(logo_path)
            
            # Redimensionar el logo manteniendo la relación de aspecto
            max_size = (100, 100)
            logo.thumbnail(max_size, Image.LANCZOS)  # Usar Image.LANCZOS en lugar de Image.ANTIALIAS
            self.logo_image = ImageTk.PhotoImage(logo)
            
            logo_label = ttk.Label(main_frame, image=self.logo_image)
            logo_label.grid(row=0, column=0, columnspan=2, pady=10)
        except Exception as e:
            print(f"Error al cargar el logo: {str(e)}")

        # Etiqueta y entrada para URL base
        url_label = ttk.Label(main_frame, text="URL base de MercadoLibre:")
        url_label.grid(row=1, column=0, sticky=tk.W, pady=10)
        self.url_entry = ttk.Entry(main_frame, width=50)
        self.url_entry.grid(row=1, column=1, padx=10, pady=10)

        # Etiqueta y entrada para fechas específicas
        fechas_label = ttk.Label(main_frame, text="Fechas específicas (separadas por coma):")
        fechas_label.grid(row=2, column=0, sticky=tk.W, pady=10)
        self.fechas_entry = ttk.Entry(main_frame, width=50)
        self.fechas_entry.grid(row=2, column=1, padx=10, pady=10)

        # Botón para iniciar el proceso
        start_button = ttk.Button(main_frame, text="Iniciar Extracción", command=self.start_extraction)
        start_button.grid(row=3, column=0, columnspan=2, pady=20)

    def start_extraction(self):
        url_base = self.url_entry.get()
        fechas_especificas = [fecha.strip() for fecha in self.fechas_entry.get().split(",")]

        if url_base and fechas_especificas:
            self.main_process(url_base, fechas_especificas)
        else:
            messagebox.showerror("Error", "Por favor ingresa la URL base y las fechas específicas.")

def main_process(url_base, fechas_especificas):
    print(f"URL base: {url_base}")
    print(f"Fechas específicas: {fechas_especificas}")
    # Aquí iría la lógica principal de extracción de datos

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Extracción de Datos MercadoLibre")
    main_window = MainWindow(root, main_process)
    root.mainloop()
