# ===========================================================================================
# ui_splash.py
# -------------------------------------------------------------------------------------------
# Módulo para la pantalla de carga inicial (Splash Screen) de KlarityFinanzasApp.
# Muestra logo, barra de progreso y slogan antes de arrancar la aplicación principal.
# ===========================================================================================

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk                   # Pillow para abrir y mostrar imágenes
from constants import (                           # Variables de estilo globales
    COLOR_PRINCIPAL_AZUL,
    COLOR_VERDE_CRECIMIENTO,
    COLOR_FONDO_GRIS,
    COLOR_BLANCO,
    FONT_TITLE,
    FONT_SLOGAN,
    APP_SLOGAN
)
from utils import center_window                   # Función para centrar la ventana en pantalla

class SplashScreen:
    """
    Clase que gestiona la ventana de Splash Screen.
    
    Parámetros:
    - root: la ventana raíz de Tkinter (oculta).
    - on_finish: callback a ejecutar cuando termine la animación.
    """
    def __init__(self, root: tk.Tk, on_finish):
        self.root = root
        self.on_finish = on_finish
        
        # Creamos una nueva ventana de nivel superior
        self.win = tk.Toplevel(root)
        # Quitamos bordes y barra de título para un aspecto limpio
        self.win.overrideredirect(True)
        # Color de fondo principal
        self.win.configure(bg=COLOR_PRINCIPAL_AZUL)
        # Centrar la ventana con tamaño fijo 420×420 px
        center_window(self.win, 420, 420)
        
        # Construir los widgets de la splash
        self._build()

    def _build(self):
        """
        Configura y empaqueta todos los widgets dentro de la ventana:
        - Logo (imagen o “K” si no está disponible)
        - Texto de título y mensaje de “Cargando...”
        - Barra de progreso animada
        - Slogan de la aplicación
        """
        # Contenedor principal dentro de la ventana
        frame = tk.Frame(self.win, bg=COLOR_PRINCIPAL_AZUL)
        frame.pack(expand=True)
        
        # Intentar cargar y mostrar el logo desde assets/klarity_logo.png
        try:
            img = Image.open("assets/klarity_logo.png").resize((150, 150))
            photo = ImageTk.PhotoImage(img)
            lbl_img = tk.Label(frame, image=photo, bg=COLOR_PRINCIPAL_AZUL)
            lbl_img.image = photo              # Mantener referencia para evitar GC
            lbl_img.pack(pady=10)
        except FileNotFoundError:
            # Si no existe el archivo, mostramos una letra como placeholder
            tk.Label(
                frame,
                text="K",
                font=("Lato", 80, "bold"),
                fg=COLOR_BLANCO,
                bg=COLOR_PRINCIPAL_AZUL
            ).pack()

        # Título de la app debajo del logo
        tk.Label(
            frame,
            text="Klarity",
            font=FONT_TITLE,
            fg=COLOR_BLANCO,
            bg=COLOR_PRINCIPAL_AZUL
        ).pack()
        
        # Mensaje de carga
        tk.Label(
            frame,
            text="Cargando...",
            fg=COLOR_FONDO_GRIS,
            bg=COLOR_PRINCIPAL_AZUL
        ).pack(pady=5)

        # ─── Barra de progreso ──────────────────────────────────────────
        style = ttk.Style()
        style.theme_use("clam")  # Tema “clam” para permitir personalización
        style.configure(
            "green.Horizontal.TProgressbar",
            foreground=COLOR_VERDE_CRECIMIENTO,
            background=COLOR_VERDE_CRECIMIENTO
        )
        # Creamos el widget Progressbar en modo determinate (0–100)
        self.pb = ttk.Progressbar(
            frame,
            length=300,
            mode="determinate",
            style="green.Horizontal.TProgressbar"
        )
        self.pb.pack(pady=20)

        # Slogan de la aplicación al pie de la splash
        tk.Label(
            frame,
            text=APP_SLOGAN,
            fg=COLOR_FONDO_GRIS,
            bg=COLOR_PRINCIPAL_AZUL,
            font=FONT_SLOGAN
        ).pack(pady=5)

        # Iniciamos la animación de la barra de progreso
        self._animate()

    def _animate(self, step=0):
        """
        Función recursiva para animar la barra de progreso.
        - Aumenta `step` de 0 a 100 en incrementos de 2.
        - Cada 25 ms avanza un poco, hasta completar.
        - Al llegar a 100, destruye la ventana y llama a on_finish().
        """
        if step <= 100:
            self.pb["value"] = step
            # Programar siguiente actualización tras 25 ms
            self.win.after(25, lambda: self._animate(step + 2))
        else:
            # Cuando termina, cerrar splash y notificar
            self.win.destroy()
            self.on_finish()

    def show(self):
        """
        Método público para mostrar la splash.
        Normalmente se llama justo antes de mainloop.
        """
        self.win.deiconify()
