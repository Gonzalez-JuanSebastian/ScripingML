import tkinter as tk
from tkinter import ttk
from gui.main_window import MainWindow
from mapeoML import main_process

def main():
    root = tk.Tk()
    root.title("AbinML - Extractor de Datos de MercadoLibre")
    main_window = MainWindow(root, main_process)
    root.mainloop()

if __name__ == "__main__":
    main()
