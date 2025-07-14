# ===========================================================================================
# utils.py – KlarityFinanzasApp
# -------------------------------------------------------------------------------------------
# Módulo de utilidades que agrupa funciones genéricas para:
# - Limpiar contenedores de widgets en Tkinter.
# - Centrar ventanas en pantalla.
# - Formatear números como cadenas monetarias en pesos colombianos (COP).
# ===========================================================================================

import tkinter as tk

def clear_frame(frame: tk.Frame) -> None:
    """
    Elimina todos los widgets hijos de un contenedor Tkinter.

    Parámetros:
    - frame: instancia de tk.Frame cuyo contenido debe borrarse.

    Uso típico:
        # Antes de reconstruir una sección dinámica de la UI:
        clear_frame(mi_frame)
        # A continuación, volvemos a crear los widgets deseados en 'mi_frame'.
    """
    for w in frame.winfo_children():
        w.destroy()  # Cada widget hijo es destruido, liberando espacio y memoria.


def center_window(win: tk.Toplevel, width: int = None, height: int = None) -> None:
    """
    Centra una ventana Toplevel en la pantalla del usuario.

    Parámetros:
    - win: instancia de tk.Toplevel (o tk.Tk) a centrar.
    - width, height: dimensiones deseadas en píxeles.
        Si no se especifican, se usan las dimensiones actuales de la ventana.

    Funcionamiento:
    1. win.update_idletasks() fuerza el cálculo de tamaño actual.
    2. Si no se dan width/height, los toma de win.winfo_width()/winfo_height().
    3. Calcula x,y para colocar la esquina superior izquierda de modo
       que la ventana quede centrada en el monitor.
    4. Ajusta la geometría con win.geometry().
    """
    # Asegurarnos de que el tamaño interno esté actualizado
    win.update_idletasks()

    # Si no se pasan dimensiones, obtenemos las actuales
    if width is None or height is None:
        width  = win.winfo_width()
        height = win.winfo_height()

    # Cálculo de posición para centrar
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    x = (screen_w  // 2) - (width  // 2)
    y = (screen_h // 2) - (height // 2)

    # Aplicar geometría "ancho x alto + x + y"
    win.geometry(f"{width}x{height}+{x}+{y}")


def money(value: float) -> str:
    """
    Formatea un número como cadena monetaria en COP (Pesos Colombianos).

    Parámetros:
    - value: valor numérico (float o int) que representa una cantidad monetaria.

    Retorna:
    - Una cadena con separadores de miles con punto, sin decimales.

    Ejemplo:
        >>> money(1234567.89)
        '$1.234.568'
    """
    # formateo con coma para miles y luego convertimos comas a puntos
    formatted = f"${value:,.0f}".replace(",", ".")
    return formatted
