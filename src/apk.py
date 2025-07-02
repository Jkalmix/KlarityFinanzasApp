# src/main.py
#pip install -r requirements.txt
#pip install firebase_admin
#pip install pillow
#pip install pyrebase4
#pip install firebase
# =================================================================================
# 1. IMPORTACIONES DE LIBRERÍAS
# =================================================================================
# tkinter: Es la librería estándar de Python para crear interfaces gráficas de usuario (GUI).
# messagebox: Un módulo de tkinter para mostrar ventanas de diálogo (errores, información, etc.).
# ttk: ("themed tkinter") Proporciona widgets con un aspecto más moderno que los de tkinter base.
# PIL (Pillow): Se usa para abrir, manipular y mostrar imágenes como el logo (.png).
# =================================================================================
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkinter import messagebox, ttk
from PIL import Image, ImageTk

import os  # Necesario para clear_screen si lo usas (aunque en GUI no es común, lo dejé en el ejemplo anterior)
import time # Necesario para timestamps (fecha de registro)

# IMPORTACIÓN CLAVE: Importamos el módulo que maneja las interacciones con Firebase.
#  'firebase_service.py' esta en el mismo directorio 'src'.
import firebase_service

# =================================================================================
# 2. DEFINICIÓN DE LA IDENTIDAD VISUAL
# =================================================================================
# Centralizar colores y fuentes hace que la aplicación sea fácil de mantener.
# --- PALETA DE COLORES ---
COLOR_PRINCIPAL_AZUL = "#2C3E50"  # Azul oscuro para fondos y elementos principales.
COLOR_VERDE_CRECIMIENTO = "#2ECC71"  # Verde para botones de acción positiva (login, registro).
COLOR_ROJO_GASTO = "#E74C3C"      # Rojo para alertas o acciones negativas (cerrar sesión).
COLOR_FONDO_GRIS = "#ECF0F1"      # Gris claro para el fondo general de las ventanas.
COLOR_TEXTO_GRIS = "#34495E"      # Gris oscuro para la mayoría de los textos.
COLOR_BLANCO = "#FFFFFF"            # Blanco para texto sobre fondos oscuros.
COLOR_LINK_AZUL = "#3498DB"       # Un azul más brillante para los enlaces.

# --- TIPOGRAFÍA ---
# Se define la familia de fuente "Lato" y tamaños estándar para títulos y texto normal.
# Es crucial que la fuente "Lato" esté instalada en el sistema operativo.
FONT_BOLD = ("Lato", 16, "bold")
FONT_TITLE = ("Lato", 24, "bold")
FONT_NORMAL = ("Lato", 12)
FONT_SLOGAN = ("Lato", 14, "italic")
FONT_MENU = ("Lato", 14)

# =================================================================================
# 3. CONSTANTES Y VARIABLES GLOBALES
# =================================================================================
# El slogan se define aquí para que sea fácil de cambiar.
SLOGAN_APP = "Finanzas claras, Futuro Seguro."

# --- VENTANA RAÍZ (ROOT) ---
# tk.Tk() crea la ventana principal que actúa como la base de toda la aplicación.
root = tk.Tk()
# root.withdraw() oculta esta ventana base. La usaremos solo como un motor en segundo
# plano para mantener las otras ventanas (Toplevel) funcionando.
root.withdraw()

# Definimos variables globales para las ventanas y widgets. Esto nos permite
# acceder a ellos desde diferentes funciones 
login_window = None
home_window = None
registro_window = None # Ventana para el registro.

# Widgets de Login
email_entry = None
password_entry = None
show_password_login_var = None # Variable para el Checkbutton de mostrar/ocultar contraseña en login

# Widgets de Registro
nombre_entry = None
email_registro_entry = None
password_registro_entry = None
confirm_password_entry = None
show_password_registro_var = None # Variable para el Checkbutton de mostrar/ocultar contraseña en registro
show_confirm_password_registro_var = None # Variable para el Checkbutton de mostrar/ocultar confirmar contraseña en registro

# Variable global para esta nueva ventana
auth_landing_window = None # Variable para la pantalla principal de autenticación

# Variable global para almacenar el objeto del usuario actualmente logueado en Firebase.
# `None` significa que no hay nadie logueado. Contendrá el diccionario de usuario de Pyrebase
# si el login es exitoso (ej. {'email': '...', 'localId': 'UID_DEL_USUARIO', ...}).
current_user = None

# =================================================================================
# 4. FUNCIONES DE LÓGICA DE LA APLICACIÓN
# =================================================================================

def intentar_login():
    """
    Función que maneja el intento de inicio de sesión del usuario.
    Utiliza la función `firebase_service.login_user` para autenticarse con Firebase.
    """
    global current_user 

    email = email_entry.get()
    password = password_entry.get()

    # Validación básica de campos no vacíos antes de enviar a Firebase.
    if not email or not password:
        messagebox.showerror("Error de Login", "Por favor, introduce tu email y contraseña.", parent=login_window)
        return

    # --- INTEGRACIÓN CON FIREBASE SERVICE ---
    # Llama a la función de login del módulo firebase_service.
    # Esta función devuelve el objeto de usuario y un mensaje de error (si lo hay).
    user, error = firebase_service.login_user(email, password)

    if user:
        # Si el login es exitoso, almacenamos el objeto de usuario.
        current_user = user 
        messagebox.showinfo("Login Exitoso", f"¡Bienvenido/a a Klarity, {current_user['email']}!", parent=login_window) # 
        login_window.destroy()  # Cierra la ventana de login.
        mostrar_home()          # Abre la pantalla principal de la aplicación.
    else:
        # Si hay un error, lo mostramos en un messagebox.
        messagebox.showerror("Error de Login", error, parent=login_window) 

def intentar_registro():
    """
    Función que maneja el intento de registro de un nuevo usuario.
    Ahora utiliza la función `firebase_service.register_user` para crear el usuario en Firebase
    y `firebase_service.create_user_profile` para guardar un perfil inicial.
    """
    global current_user 

    nombre = nombre_entry.get()
    email = email_registro_entry.get()
    password = password_registro_entry.get()
    confirm_password = confirm_password_entry.get()

    # --- Validaciones de entrada de datos en la GUI ---
    if not nombre or not email or not password or not confirm_password:
        messagebox.showerror("Error de Registro", "Todos los campos son obligatorios.", parent=registro_window)
        return

    if password != confirm_password:
        messagebox.showerror("Error de Registro", "Las contraseñas no coinciden.", parent=registro_window)
        return

    # También puedes añadir validación de formato de email o longitud de contraseña aquí antes de enviar a Firebase.
    if len(password) < 6: 
        messagebox.showerror("Error de Registro", "La contraseña debe tener al menos 6 caracteres.", parent=registro_window)
        return


    # --- INTEGRACIÓN CON FIREBASE SERVICE ---
    # Llama a la función de registro de usuario en Firebase Authentication.
    user, error = firebase_service.register_user(email, password)

    if user:
        # Si el registro en Auth es exitoso, logueamos al usuario automáticamente
        # y creamos un perfil inicial en Realtime Database.
        current_user = user 
        messagebox.showinfo("Registro Exitoso", "¡Tu cuenta ha sido creada y has iniciado sesión!", parent=registro_window)

        # Datos iniciales para el perfil del usuario en Realtime Database
        profile_data = { 
            "email": user['email'],
            "nombre": nombre, # Usamos el nombre que el usuario proporcionó
            "saldo_inicial": 0.0, # Saldo inicial por defecto
            "fecha_registro": time.time() # Añadimos un timestamp de registro
        }
        # Crea el perfil en la base de datos usando el UID del usuario.
        profile_success, profile_msg = firebase_service.create_user_profile(user['localId'], profile_data) 
        if profile_success: 
            print(f"Perfil de usuario creado en DB: {profile_msg}")
        else:
            print(f"Error al crear perfil en DB: {profile_msg}")
            messagebox.showwarning("Advertencia", "Tu cuenta fue creada, pero hubo un problema al guardar tu perfil inicial. Podrás editarlo más tarde.", parent=registro_window)

        registro_window.destroy() # Cerramos la ventana de registro.
        mostrar_home()            # Mostramos la ventana principal.
    else:
        # Si hay un error durante el registro en Auth, lo mostramos.
        messagebox.showerror("Error de Registro", error, parent=registro_window)

def cerrar_sesion():
    """
    Función para el botón "Cerrar Sesión" en la ventana Home.
    Limpia el usuario actual y redirige a la ventana de login.
    """
    global current_user
    current_user = None # Desvincula al usuario de la sesión actual.
    home_window.destroy() # Cierra la ventana principal (Home).
    mostrar_login_window() # Muestra la ventana de login.
    messagebox.showinfo("Sesión Cerrada", "Has cerrado sesión correctamente.")

def toggle_password_visibility(password_entry_widget, check_button_var):
    """
    Función para alternar la visibilidad de la contraseña en un campo de entrada.
    Cambia el atributo 'show' del Entry widget.
    """
    if check_button_var.get():
        password_entry_widget.config(show="") # Muestra el texto
    else:
        password_entry_widget.config(show="*") # Oculta el texto con asteriscos

# =================================================================================
# 5. FUNCIONES PARA CREAR LAS VENTANAS DE LA APLICACIÓN
# =================================================================================
# Separar la creación de cada ventana en su propia función hace el código más
# ordenado y legible.

def mostrar_home():
    """
    Crea y muestra la ventana principal (Dashboard) de la aplicación 'Klarity'.
    Esta ventana está diseñada con un menú de navegación lateral y un área de contenido principal
    que se actualiza dinámicamente al seleccionar opciones del menú.

    Estructura de la ventana:
    - Un Frame lateral izquierdo para el menú de navegación (COLOR_PRINCIPAL_AZUL).
    - Un Frame principal a la derecha para mostrar el contenido de cada sección (COLOR_FONDO_GRIS).

    Funcionalidades:
    - Saludo personalizado al usuario logueado.
    - Botones en el menú lateral para navegar entre "Dashboard", "Transacciones",
      "Categorías", "Reportes" y "Perfil".
    - Un botón "Cerrar Sesión" en la parte inferior del menú lateral.
    - El área de contenido principal se actualiza llamando a funciones específicas
      (ej. `mostrar_dashboard_contenido`, `mostrar_transacciones`).
    - Manejo del logo de la aplicación.
    """
    global home_window, frame_contenido # Se declaran como globales para poder acceder a ellas.
    #'frame_contenido' es crucial para cambiar el contenido.

    home_window = tk.Toplevel(root)
    home_window.title("Klarity - Dashboard")
    home_window.geometry("1024x720")  # Aumentamos el tamaño para una mejor distribución de elementos.
    home_window.configure(bg=COLOR_FONDO_GRIS)
    home_window.resizable(True, True) # Permitir redimensionar la ventana si se desea.

    # 1. Crear el Frame para el menú lateral (izquierda),
    # tk.Frame(): Crea un widget Frame, que es un contenedor rectangular que se usa para organizar otros widgets.
    # (home_window, ...): Indica que frame_menu_lateral es un hijo de home_window
    frame_menu_lateral = tk.Frame(home_window, bg=COLOR_PRINCIPAL_AZUL, width=220)

    # .pack(): Es uno de los gestores de geometría de Tkinter.
    # Organiza los widgets en bloques antes de colocarlos en el widget padre.
    # 'side="left"' lo ancla a la izquierda. 'fill="y"' hace que se expanda verticalmente.
    frame_menu_lateral.pack(side="left", fill="y")

    # 'pack_propagate(False)' evita que el frame se encoja o expanda para ajustarse a sus contenidos,
    #Por defecto, un Frame se encogerá o expandirá para ajustarse a sus widgets hijos.
    # manteniendo el 'width' fijo.
    # False para que no ajuste su tamaño basándose en sus hijos, sino que mantenga su tamaño
    frame_menu_lateral.pack_propagate(False)

    # 2. Crear el Frame para el contenido principal (derecha) tk.Frame(home_window, ...): Es hijo de home_window.
    frame_contenido = tk.Frame(home_window, bg=COLOR_FONDO_GRIS)
    # .pack(): Empaqueta este frame.
    # 'side="right"' lo ancla a la derecha (ocupando el espacio restante).
    # 'fill="both"' lo expande tanto horizontal como verticalmente.
    # 'expand=True' hace que ocupe todo el espacio disponible al redimensionar la ventana.
    frame_contenido.pack(side="right", fill="both", expand=True)

    # --- Contenido del Menú Lateral ---

    # Logo o nombre de la aplicación en la parte superior del menú
    try: # si el archivo del logo no se encuentra), entonces ejecuta el código dentro del bloque except
        # Carga y redimensiona el logo 'assets/klarity_logo.png'.
        logo_menu_image = Image.open("assets/klarity_logo.png").resize((80, 80), Image.Resampling.LANCZOS)
        logo_menu_photo = ImageTk.PhotoImage(logo_menu_image)
        #tk.Label(): Crea un widget de etiqueta. (frame_menu_lateral, ...): Es hijo del frame del menú lateral.
        label_logo_menu = tk.Label(frame_menu_lateral, image=logo_menu_photo, bg=COLOR_PRINCIPAL_AZUL)
        label_logo_menu.image = logo_menu_photo # Importante para evitar que la imagen sea eliminada por el garbage collector.
        label_logo_menu.pack(pady=(20, 10))
    except FileNotFoundError:
        # Alternativa si el logo no se encuentra.
        tk.Label(frame_menu_lateral, text="Klarity", font=FONT_BOLD, fg=COLOR_BLANCO, bg=COLOR_PRINCIPAL_AZUL).pack(pady=(20, 10))

   

    # ──────────────────────────────────────────────────────────────
    #  LOGO  +  TÍTULO  DEL  MENÚ
    # ──────────────────────────────────────────────────────────────

    # ──────────────────────────────────────────────────────────────
    #  LOGO  +  TÍTULO  DEL  MENÚ
    # ──────────────────────────────────────────────────────────────


    tk.Label(frame_menu_lateral, text="Menú", font=FONT_BOLD,
             bg=COLOR_PRINCIPAL_AZUL, fg=COLOR_BLANCO).pack(pady=(0, 20))

    # Opcional: elimina borde interno que Windows agrega a ttk.Button
    root.option_add("*TButton*HighlightThickness", 0)
    # Opcional: sin sangría interna en el frame
    frame_menu_lateral.configure(padx=0)

    # ──────────────────────────────────────────────────────────────
    #  ESTILOS ttk
    # ──────────────────────────────────────────────────────────────
    style = ttk.Style()
    style.theme_use("clam")

    # estándar
    style.configure("Sidebar.TButton",
                    font=FONT_MENU,
                    background=COLOR_PRINCIPAL_AZUL,
                    foreground=COLOR_BLANCO,
                    anchor="w",
                    padding=(14, 8),
                    relief="flat",
                    borderwidth=0,
                    focusthickness=0)
    style.map("Sidebar.TButton",
              background=[("active", "#1f4a72")])

    # seleccionado
    style.configure("Sidebar.Selected.TButton",
                    font=FONT_MENU,
                    background=COLOR_VERDE_CRECIMIENTO,
                    foreground=COLOR_BLANCO,
                    anchor="w",
                    padding=(14, 8),
                    relief="flat",
                    borderwidth=0,
                    focusthickness=0)

    # peligro (Cerrar sesión)
    style.configure("Sidebar.Danger.TButton",
                    font=FONT_MENU,
                    background=COLOR_ROJO_GASTO,
                    foreground=COLOR_BLANCO,
                    anchor="center",
                    padding=(14, 8),
                    relief="flat",
                    borderwidth=0,
                    focusthickness=0)
    style.map("Sidebar.Danger.TButton",
              background=[("active", "#c0392b")])

    # ──────────────────────────────────────────────────────────────
    #  ITEMS DEL MENÚ  (texto, función)
    # ──────────────────────────────────────────────────────────────
    NAV_ITEMS = [
        ("Dashboard",     mostrar_dashboard_contenido),
        ("Transacciones", mostrar_transacciones),
        ("Categorías",    mostrar_categorias),
        ("Reportes",      mostrar_reportes),
        ("Perfil",        mostrar_perfil),
    ]

    # ──────────────────────────────────────────────────────────────
    #  CREACIÓN  DINÁMICA  DE  BOTONES
    # ──────────────────────────────────────────────────────────────
    btn_refs = {}
    selected_btn = None

    def navegar(nombre, accion):
        nonlocal selected_btn
        accion()                                         # pinta la vista
        if selected_btn:
            selected_btn.configure(style="Sidebar.TButton")
        btn_refs[nombre].configure(style="Sidebar.Selected.TButton")
        selected_btn = btn_refs[nombre]

    for texto, funcion in NAV_ITEMS:
        btn = ttk.Button(frame_menu_lateral,
                         text=texto,
                         style="Sidebar.TButton",
                         command=lambda t=texto, f=funcion: navegar(t, f))
        btn.pack(fill="x", pady=2)
        btn_refs[texto] = btn

    # ──────────────────────────────────────────────────────────────
    #  BOTÓN  CERRAR  SESIÓN
    # ──────────────────────────────────────────────────────────────
    ttk.Button(frame_menu_lateral, text="Cerrar Sesión",
               style="Sidebar.Danger.TButton",
               command=cerrar_sesion).pack(side="bottom",
                                           fill="x", pady=20, padx=10)

    # Vista inicial + cierre correcto con la X
    mostrar_dashboard_contenido()
    home_window.protocol("WM_DELETE_WINDOW", root.destroy)

# ================================================================================
#  Funciones de contenido  (frame_contenido)
# ================================================================================

def _clear_content():
    for w in frame_contenido.winfo_children():
        w.destroy()

# ────────────────── 1 · DASHBOARD ──────────────────
def mostrar_dashboard_contenido():
    _clear_content()
    email = current_user["email"] if current_user else "Usuario"
    tk.Label(frame_contenido, text=f"¡Bienvenido/a, {email}!",
             font=FONT_TITLE, bg=COLOR_FONDO_GRIS,
             fg=COLOR_PRINCIPAL_AZUL).pack(pady=(20, 10))
    tk.Label(frame_contenido, text="Resumen general de tus finanzas",
             font=FONT_NORMAL, bg=COLOR_FONDO_GRIS,
             fg=COLOR_TEXTO_GRIS).pack()

    fig, ax = plt.subplots(figsize=(5, 2.5))
    ax.bar(["Ene", "Feb", "Mar"], [200, 150, 300], width=0.6,
           linewidth=0, edgecolor="none")
    ax.set_title("Saldo mensual"); ax.set_ylabel("$"); ax.grid(axis="y")
    canvas = FigureCanvasTkAgg(fig, master=frame_contenido)
    canvas.draw(); canvas.get_tk_widget().pack(pady=20)

# ────────────────── 2 · TRANSACCIONES ───────────────
def mostrar_transacciones():
    _clear_content()
    tk.Label(frame_contenido, text="Historial de Movimientos",
             font=FONT_TITLE, bg=COLOR_FONDO_GRIS,
             fg=COLOR_PRINCIPAL_AZUL).pack(pady=20)

    cols = ("Fecha", "Descripción", "Monto", "Tipo", "Categoría")
    tree = ttk.Treeview(frame_contenido, columns=cols,
                        show="headings", height=12)
    for c in cols:
        tree.heading(c, text=c); tree.column(c, anchor="center")
    tree.pack(fill="both", expand=True, padx=20)

    dummy = [("2025-07-02", "Café", -4500, "Gasto", "Alimentos"),
             ("2025-07-02", "Pago freelance", 300000, "Ingreso", "Salario")]
    for row in dummy:
        tree.insert("", "end", values=row)

    ttk.Button(frame_contenido, text="+ Nuevo movimiento",
               command=abrir_modal_nuevo_movimiento,
               style="Sidebar.TButton").pack(pady=10)

# ────────────────── 3 · CATEGORÍAS ───────────────────
def mostrar_categorias():
    _clear_content()
    tk.Label(frame_contenido, text="Gestión de Categorías",
             font=FONT_TITLE, bg=COLOR_FONDO_GRIS,
             fg=COLOR_PRINCIPAL_AZUL).pack(pady=20)
    tk.Label(frame_contenido,
             text="(Aquí podrás añadir, editar o eliminar categorías.)",
             font=FONT_NORMAL, bg=COLOR_FONDO_GRIS,
             fg=COLOR_TEXTO_GRIS).pack()
    for cat in ["Alimentos", "Transporte", "Salario"]:
        tk.Label(frame_contenido, text=f"• {cat}",
                 font=FONT_NORMAL, bg=COLOR_FONDO_GRIS,
                 fg=COLOR_TEXTO_GRIS).pack(anchor="w", padx=40)

# ────────────────── 4 · REPORTES ─────────────────────
def mostrar_reportes():
    _clear_content()
    tk.Label(frame_contenido, text="Reportes y Análisis",
             font=FONT_TITLE, bg=COLOR_FONDO_GRIS,
             fg=COLOR_PRINCIPAL_AZUL).pack(pady=20)
    ttk.Button(frame_contenido, text="Reporte mensual de gastos").pack(pady=5)
    ttk.Button(frame_contenido, text="Flujo de caja anual").pack(pady=5)
    ttk.Button(frame_contenido, text="Balance de activos").pack(pady=5)

# ────────────────── 5 · PERFIL ───────────────────────
def mostrar_perfil():
    _clear_content()
    tk.Label(frame_contenido, text="Mi Perfil",
             font=FONT_TITLE, bg=COLOR_FONDO_GRIS,
             fg=COLOR_PRINCIPAL_AZUL).pack(pady=20)
    email = current_user["email"] if current_user else "N/A"
    tk.Label(frame_contenido, text=f"Email: {email}",
             font=FONT_NORMAL, bg=COLOR_FONDO_GRIS,
             fg=COLOR_TEXTO_GRIS).pack(pady=5)
    tk.Label(frame_contenido, text="Nombre:",
             font=FONT_NORMAL, bg=COLOR_FONDO_GRIS,
             fg=COLOR_TEXTO_GRIS).pack(pady=(15, 5))
    tk.Entry(frame_contenido, width=30).pack()
    ttk.Button(frame_contenido, text="Actualizar Perfil").pack(pady=15)

# ────────────────── MODAL (+Movimiento) ──────────────
def abrir_modal_nuevo_movimiento():
    modal = tk.Toplevel(home_window)
    modal.title("Nuevo Movimiento"); modal.grab_set()
    modal.resizable(False, False)
    tk.Label(modal, text="Descripción:").grid(row=0, column=0,
                                              sticky="e", pady=5, padx=5)
    desc = tk.Entry(modal, width=30); desc.grid(row=0, column=1)
    tk.Label(modal, text="Monto:").grid(row=1, column=0,
                                        sticky="e", pady=5, padx=5)
    monto = tk.Entry(modal, width=30); monto.grid(row=1, column=1)
    tipo = tk.StringVar(value="Gasto")
    ttk.Radiobutton(modal, text="Ingreso", variable=tipo,
                    value="Ingreso").grid(row=2, column=0, pady=5, padx=5)
    ttk.Radiobutton(modal, text="Gasto", variable=tipo,
                    value="Gasto").grid(row=2, column=1, pady=5, padx=5)
    ttk.Button(modal, text="Guardar",
               command=lambda: [modal.destroy(),
                                mostrar_transacciones()]).grid(row=3,
                                                               columnspan=2,
                                                               pady=15)







def mostrar_registro_window():
    """Crea y muestra la ventana de Registro de nuevo usuario con opción de mostrar/ocultar contraseña."""
    global registro_window, nombre_entry, email_registro_entry, password_registro_entry, confirm_password_entry, show_password_registro_var, show_confirm_password_registro_var
    registro_window = tk.Toplevel(root) # Crea una nueva ventana de nivel superior. 
    #Esta es una ventana independiente que aparece "encima" de otras ventanas.
    registro_window.title("Klarity - Crear Cuenta")
    registro_window.geometry("400x750") # Ajusta el tamaño para el Checkbutton
    registro_window.configure(bg=COLOR_FONDO_GRIS)
    registro_window.resizable(False, False)
    try:
        imagen_original = Image.open("assets/klarity_logo.png")  # 
        imagen_redimensionada = imagen_original.resize((80, 80))  # Ajusta el tamaño del logo
        logo = ImageTk.PhotoImage(imagen_redimensionada)

        # Creamos un Label para mostrar la imagen
        label_logo = tk.Label(registro_window, image=logo)
        label_logo.image = logo  # ¡Importante! Evita que la imagen sea recolectada por el recolector de basura
        label_logo.pack(pady=10)
    except Exception as e:
        print(f"No se pudo cargar el logo: {e}")
    # --- Widgets de la ventana de Registro ---
    tk.Label(registro_window, text="Crear Nueva Cuenta", font=FONT_BOLD, bg=COLOR_FONDO_GRIS, fg=COLOR_PRINCIPAL_AZUL).pack(pady=(20, 10))
    
    # Campo para el Nombre
    tk.Label(registro_window, text="Nombre Completo:", font=FONT_NORMAL, bg=COLOR_FONDO_GRIS, fg=COLOR_TEXTO_GRIS).pack(pady=(10, 5))
    nombre_entry = tk.Entry(registro_window, width=35, font=FONT_NORMAL, relief="flat", highlightbackground=COLOR_TEXTO_GRIS, highlightthickness=1)
    nombre_entry.pack()

    # Campo para el Email
    tk.Label(registro_window, text="Email:", font=FONT_NORMAL, bg=COLOR_FONDO_GRIS, fg=COLOR_TEXTO_GRIS).pack(pady=(10, 5))
    email_registro_entry = tk.Entry(registro_window, width=35, font=FONT_NORMAL, relief="flat", highlightbackground=COLOR_TEXTO_GRIS, highlightthickness=1)
    email_registro_entry.pack()

    # Campo para la Contraseña
    tk.Label(registro_window, text="Contraseña:", font=FONT_NORMAL, bg=COLOR_FONDO_GRIS, fg=COLOR_TEXTO_GRIS).pack(pady=(10, 5))
    password_registro_entry = tk.Entry(registro_window, width=35, font=FONT_NORMAL, show="*", relief="flat", highlightbackground=COLOR_TEXTO_GRIS, highlightthickness=1)
    password_registro_entry.pack()

    # Checkbutton para mostrar/ocultar contraseña de registro
    # tk.BooleanVar() Crea una variable de control de Tkinter que puede contener un valor booleano (True o False). 
    # Esta variable se vinculará al estado del Checkbutton. Cuando el Checkbutton está marcado, 
    # el valor es True; cuando no está marcado, es False
    show_password_registro_var = tk.BooleanVar() # Variable de control para el estado del Checkbutton
    check_show_password_registro = tk.Checkbutton(registro_window, text="Mostrar Contraseña",
                                                 variable=show_password_registro_var,
                                                 command=lambda: toggle_password_visibility(password_registro_entry, show_password_registro_var),
                                                 bg=COLOR_FONDO_GRIS, fg=COLOR_TEXTO_GRIS, font=FONT_NORMAL,
                                                 selectcolor=COLOR_FONDO_GRIS) # Color de fondo cuando está seleccionado
    check_show_password_registro.pack(anchor="w", padx=25) # Alineado a la izquierda

    # Campo para Confirmar Contraseña
    tk.Label(registro_window, text="Confirmar Contraseña:", font=FONT_NORMAL, bg=COLOR_FONDO_GRIS, fg=COLOR_TEXTO_GRIS).pack(pady=(10, 5))
    confirm_password_entry = tk.Entry(registro_window, width=35, font=FONT_NORMAL, show="*", relief="flat", highlightbackground=COLOR_TEXTO_GRIS, highlightthickness=1)
    confirm_password_entry.pack()

    # Checkbutton para mostrar/ocultar confirmar contraseña de registro
    show_confirm_password_registro_var = tk.BooleanVar() # Variable de control
    check_show_confirm_password_registro = tk.Checkbutton(registro_window, text="Mostrar Contraseña",
                                                 variable=show_confirm_password_registro_var,
                                                 command=lambda: toggle_password_visibility(confirm_password_entry, show_confirm_password_registro_var),
                                                 bg=COLOR_FONDO_GRIS, fg=COLOR_TEXTO_GRIS, font=FONT_NORMAL,
                                                 selectcolor=COLOR_FONDO_GRIS)
    check_show_confirm_password_registro.pack(anchor="w", padx=25) # Alineado a la izquierda

    # Botón para registrar la cuenta
    tk.Button(registro_window, text="Registrar Cuenta", font=FONT_NORMAL, bg=COLOR_VERDE_CRECIMIENTO, fg=COLOR_BLANCO, command=intentar_registro, relief="flat", padx=20, pady=5).pack(pady=20)
    
    # --- Enlace para volver al Login ---
    # Usamos un Frame para agrupar los dos textos del enlace.
    frame_login = tk.Frame(registro_window, bg=COLOR_FONDO_GRIS)
    frame_login.pack(pady=10)
    tk.Label(frame_login, text="¿Ya tienes una cuenta?", font=FONT_NORMAL, bg=COLOR_FONDO_GRIS, fg=COLOR_TEXTO_GRIS).pack(side="left")
    # Este Label simula un enlace.
    link_login = tk.Label(frame_login, text="Inicia Sesión", font=FONT_NORMAL, bg=COLOR_FONDO_GRIS, fg=COLOR_LINK_AZUL, cursor="hand2")
    link_login.pack(side="left", padx=5)
    # .bind() asocia un evento (clic izquierdo del ratón) con una función.
    link_login.bind("<Button-1>", lambda e: [registro_window.destroy(), mostrar_login_window()])

    registro_window.protocol("WM_DELETE_WINDOW", root.destroy)


def mostrar_login_window():
    """Crea y muestra la ventana de Login, con opción de mostrar/ocultar contraseña y enlace a registro."""

    global login_window, email_entry, password_entry, show_password_login_var
    login_window = tk.Toplevel(root)
    login_window.title("Klarity - Iniciar Sesión")
    login_window.geometry("400x600") # Ajusta el tamaño para el Checkbutton
    login_window.configure(bg=COLOR_FONDO_GRIS)
    login_window.resizable(False, False)

    # --- Widgets de la ventana de Login ---
    # --- Cargar y mostrar la imagen del logo ---
    try:
        imagen_original = Image.open("assets/klarity_logo.png")  # 
        imagen_redimensionada = imagen_original.resize((150, 150))  # Ajusta el tamaño del logo
        logo = ImageTk.PhotoImage(imagen_redimensionada)

        # Creamos un Label para mostrar la imagen
        label_logo = tk.Label(login_window, image=logo)
        label_logo.image = logo  # ¡Importante! Evita que la imagen sea recolectada por el recolector de basura
        label_logo.pack(pady=10)
    except Exception as e:
        print(f"No se pudo cargar el logo: {e}")

    # Label para el título "Iniciar Sesión".
    tk.Label(login_window, text="Iniciar Sesión", font=FONT_BOLD, bg=COLOR_FONDO_GRIS, fg=COLOR_PRINCIPAL_AZUL).pack(pady=(20, 10))
    # Campo para el Email.
    tk.Label(login_window, text="Email:", font=FONT_NORMAL, bg=COLOR_FONDO_GRIS, fg=COLOR_TEXTO_GRIS).pack(pady=(10, 5))
    # Entry es el campo de texto para que el usuario escriba.
    # 'relief="flat"' quita el borde hundido por defecto, dando un look más moderno.
    email_entry = tk.Entry(login_window, width=35, font=FONT_NORMAL, relief="flat", highlightbackground=COLOR_TEXTO_GRIS, highlightthickness=1)
    email_entry.pack()
# Campo para la Contraseña.
    tk.Label(login_window, text="Contraseña:", font=FONT_NORMAL, bg=COLOR_FONDO_GRIS, fg=COLOR_TEXTO_GRIS).pack(pady=(10, 5))
    # 'show="*"' hace que el texto escrito se muestre como asteriscos. 
    password_entry = tk.Entry(login_window, width=35, font=FONT_NORMAL, show="*", relief="flat", highlightbackground=COLOR_TEXTO_GRIS, highlightthickness=1)
    password_entry.pack()

    # Checkbutton para mostrar/ocultar contraseña en login
    show_password_login_var = tk.BooleanVar() # Variable de control para el estado del Checkbutton
    check_show_password_login = tk.Checkbutton(login_window, text="Mostrar Contraseña",
                                                 variable=show_password_login_var,
                                                 command=lambda: toggle_password_visibility(password_entry, show_password_login_var),
                                                 bg=COLOR_FONDO_GRIS, fg=COLOR_TEXTO_GRIS, font=FONT_NORMAL,
                                                 selectcolor=COLOR_FONDO_GRIS) # Color de fondo cuando está seleccionado
    check_show_password_login.pack(anchor="w", padx=25) # Alineado a la izquierda
 # Botón para iniciar sesión.
    # 'command=intentar_login' asigna la función que se ejecutará al hacer clic.
    tk.Button(login_window, text="Ingresar", font=FONT_NORMAL, bg=COLOR_VERDE_CRECIMIENTO, fg=COLOR_BLANCO, command=intentar_login, relief="flat", padx=20, pady=5).pack(pady=20)
    
    # --- Enlace para ir a la ventana de Registro ---
    # Usamos un Frame para agrupar los dos textos del enlace.
    frame_registro = tk.Frame(login_window, bg=COLOR_FONDO_GRIS)
    frame_registro.pack(pady=10)
    tk.Label(frame_registro, text="¿No tienes una cuenta?", font=FONT_NORMAL, bg=COLOR_FONDO_GRIS, fg=COLOR_TEXTO_GRIS).pack(side="left")
    # Este Label se configura para parecer y actuar como un hipervínculo.
    # fg=COLOR_LINK_AZUL le da color de enlace.
    # cursor="hand2" cambia el puntero del ratón a una mano cuando pasa por encima.
    link_registro = tk.Label(frame_registro, text="Regístrate aquí", font=FONT_NORMAL, bg=COLOR_FONDO_GRIS, fg=COLOR_LINK_AZUL, cursor="hand2")
    link_registro.pack(side="left", padx=5)
    # El evento "<Button-1>" corresponde al clic izquierdo del ratón.
    # La 'lambda' nos permite ejecutar dos comandos: cerrar la ventana actual y abrir la nueva.
    link_registro.bind("<Button-1>", lambda e: [login_window.destroy(), mostrar_registro_window()])
# Al igual que en Home, si se cierra esta ventana, la app termina
    login_window.protocol("WM_DELETE_WINDOW", root.destroy)

def mostrar_slogan_window():
    """Muestra una ventana temporal con el slogan después del splash."""
    slogan_window = tk.Toplevel(root)
    slogan_window.overrideredirect(True) # Quita los bordes y la barra de título.
    slogan_window.geometry("500x150+400+300") # "ancho x alto + pos_X + pos_Y"
    slogan_window.configure(bg=COLOR_FONDO_GRIS)
    # .pack(expand=True) hace que el widget (Label) ocupe todo el espacio disponible, centrando el texto.
    tk.Label(slogan_window, text=SLOGAN_APP, font=FONT_SLOGAN, bg=COLOR_FONDO_GRIS, fg=COLOR_PRINCIPAL_AZUL).pack(expand=True)
     # .after() espera un tiempo en milisegundos y luego ejecuta una función.
    # Aquí, espera 2.5 segundos, luego destruye la ventana del slogan y muestra la de login.
    # La 'lambda' permite ejecutar múltiples comandos en una sola llamada.
    slogan_window.after(2500, lambda: [slogan_window.destroy(), mostrar_login_window(),])

def iniciar_splash_screen():
    """Crea y gestiona la pantalla de carga inicial (Splash Screen)."""
    splash_window = tk.Toplevel(root)
    splash_window.overrideredirect(True)  # Sin bordes para un look de splash screen real.
    splash_window.geometry("400x400+450+150")
    splash_window.configure(bg=COLOR_PRINCIPAL_AZUL)
 # Usamos un Frame como contenedor para organizar y centrar fácilmente los elementos.
    frame = tk.Frame(splash_window, bg=COLOR_PRINCIPAL_AZUL)
    frame.pack(expand=True)
   # Carga del logo.
    try:
        # Abrimos la imagen, la redimensionamos y la convertimos a un formato de tkinter.
        logo_image = Image.open("assets/klarity_logo.png").resize((150, 150), Image.Resampling.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_image)
        label_logo = tk.Label(frame, image=logo_photo, bg=COLOR_PRINCIPAL_AZUL)
        label_logo.pack(pady=10)
        label_logo.image = logo_photo 
    except FileNotFoundError:
         # Si no se encuentra el logo, muestra una letra como alternativa.
        tk.Label(frame, text="K", font=("Lato", 80, "bold"), fg=COLOR_BLANCO, bg=COLOR_PRINCIPAL_AZUL).pack(pady=10)
 # Añadimos el nombre de la app y la etiqueta "Cargando...".
    tk.Label(frame, text="Klarity", font=FONT_TITLE, fg=COLOR_BLANCO, bg=COLOR_PRINCIPAL_AZUL).pack()
    tk.Label(frame, text="Cargando...", font=FONT_NORMAL, fg=COLOR_FONDO_GRIS, bg=COLOR_PRINCIPAL_AZUL).pack(pady=10)
  # --- Barra de Progreso ---
    # Creamos un estilo personalizado para la barra usando ttk.Style.
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("green.Horizontal.TProgressbar", foreground=COLOR_VERDE_CRECIMIENTO, background=COLOR_VERDE_CRECIMIENTO, troughcolor=COLOR_TEXTO_GRIS)
     # Creamos el widget de la barra de progreso con el estilo que definimos.
    progress_bar = ttk.Progressbar(frame, style="green.Horizontal.TProgressbar", orient="horizontal", length=300, mode='determinate')
    progress_bar.pack(pady=20)

    def actualizar_progreso(step=0):
        if step <= 100:
            progress_bar['value'] = step
             # Programamos la próxima ejecución de esta misma función después de 30ms.
            splash_window.after(30, lambda: actualizar_progreso(step + 2))
        else:
             # Cuando la barra llega al final, se destruye el splash y se muestra el slogan.
            splash_window.destroy()
            mostrar_slogan_window()
   # Llamamos a la función por primera vez para iniciar la animación.          
    actualizar_progreso()

# =================================================================================
# 6. INICIO DE LA APLICACIÓN
# =================================================================================
# El bloque `if __name__ == "__main__":` es una buena práctica en Python.
# Asegura que el código dentro de él solo se ejecute cuando el script es
# el programa principal, y no cuando es importado por otro script.
if __name__ == "__main__":
    iniciar_splash_screen()
    root.mainloop()
    # root.mainloop()