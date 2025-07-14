# ===========================================================================================
# main.py
# -------------------------------------------------------------------------------------------
# Punto de entrada de la aplicación KlarityFinanzasApp.
# Gestiona:
# 1. Inicialización de Tkinter (ventana raíz oculta).
# 2. Mostrado de la pantalla de carga (SplashScreen).
# 3. Tras la animación, invocación del módulo de login/registro.
# ===========================================================================================

import tkinter as tk                   # Biblioteca estándar para GUIs en Python.
from ui_splash import SplashScreen     # Clase que muestra el splash screen.
import ui_login as login               # Módulo que maneja login y registro.

def main():
    """
    - Crea la ventana raíz de Tkinter.
    - La oculta inmediatamente (root.withdraw()), porque usaremos ventanas Toplevel.
    - Define la función a ejecutar cuando termina el splash (after_splash).
    - Lanza el splash screen y arranca el loop principal de eventos.
    """
    # 1. Creamos la ventana "root" que Tkinter usa internamente.
    root = tk.Tk()
    # 2. La ocultamos porque no queremos mostrar un frame vacío.
    root.withdraw()

    # 3. Esta función se ejecutará una vez termine la animación del splash.
    def after_splash():
        # Llama al método `start` de ui_login, pasando la raíz para crear nuevas ventanas.
        login.start(root)

    # 4. Creamos y mostramos el splash screen.
    #    - Toma la ventana root como padre.
    #    - Recibe la función after_splash para llamarla al terminar.
    SplashScreen(root, after_splash).show()

    # 5. Inicia el loop de eventos de Tkinter. Hasta que todas las ventanas se cierren,
    #    este bucle mantiene la aplicación viva y responde a clicks, timers, etc.
    root.mainloop()

# -------------------------------------------------------------------------------------------
# Este bloque asegura que `main()` sólo se ejecute cuando ejecutamos
# `python main.py`, y no cuando importamos este archivo como módulo.
# -------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
