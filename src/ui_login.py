# ===========================================================================================
# ui_login.py
# -------------------------------------------------------------------------------------------
# Módulo encargado de:
# 1. Mostrar la ventana de Login (iniciar sesión).
# 2. Ofrecer la opción de mostrar/ocultar contraseña.
# 3. Enlace para ir a la ventana de Registro.
# 4. Validar campos y manejar respuestas de Firebase.
# 5. Tras login exitoso, crear categorías por defecto y pasar al Dashboard.
# ===========================================================================================

import os
import tkinter as tk                       # Biblioteca principal de GUI
from tkinter import messagebox            # Ventanas de diálogo (errores, avisos, info)
from constants import *                   # Colores, fuentes y constantes visuales
from utils import center_window           # Función auxiliar para centrar ventanas
import firebase_service as fb             # Lógica de autenticación con Firebase
import ui_dashboard as dashboard          # Módulo para mostrar el dashboard tras login

# -------------------------------------------------------------------------------------------
# Función auxiliar: alterna visibilidad de contraseña en un Entry
# -------------------------------------------------------------------------------------------

def _toggle(entry: tk.Entry, var: tk.BooleanVar):
    """
    - entry: widget de entrada de texto con atributo show.
    - var: BooleanVar que indica si mostrar (True) u ocultar (False).
    Cambia el 'show' del entry: "" para mostrar texto, "*" para ocultarlo.
    """
    entry.config(show="" if var.get() else "*")


# ===========================================================================================
# Clase LoginWindow
# -------------------------------------------------------------------------------------------
# Representa la ventana de inicio de sesión.
# Contiene logo, campos de email y contraseña, botón de login y enlace a registro.
# ===========================================================================================

class LoginWindow:
    def __init__(self, root: tk.Tk):
        """
        - root: ventana raíz oculta de Tkinter, usada como padre para este Toplevel.
        Crea la ventana, la configura y llama a _build() para poblarla.
        """
        self.root = root
        self.win = tk.Toplevel(root)                 # Nueva ventana encima de root
        self.win.title("Klarity – Iniciar Sesión")
        self.win.configure(bg=COLOR_FONDO_GRIS)       # Fondo gris claro
        center_window(self.win, 400, 600)            # Centra la ventana (400x600px)
        self._build()                                # Construye los widgets
        # Al cerrar esta ventana con la 'X', destruye root y sale de la app.
        self.win.protocol("WM_DELETE_WINDOW", root.destroy)

    def _entry(self, parent, text: str, show: str = "") -> tk.Entry:
        """
        Helper para crear un par Label+Entry:
        - parent: contenedor donde se agrega.
        - text: texto del Label.
        - show: si es "*", oculta el texto (para contraseñas).
        Retorna el widget Entry creado.
        """
        # 1. Label descriptivo encima del Entry
        tk.Label(parent,
                 text=text,
                 bg=COLOR_FONDO_GRIS,
                 fg=COLOR_TEXTO_GRIS,
                 font=FONT_NORMAL
                 ).pack(anchor="w")  # Anchor west para alinear a la izquierda

        # 2. Entry con estilo "flat" y resalte fino
        e = tk.Entry(parent,
                     width=34,
                     font=FONT_NORMAL,
                     show=show,                          # "" o "*" para ocultar
                     relief="flat",
                     highlightbackground=COLOR_TEXTO_GRIS,
                     highlightthickness=1
                     )
        e.pack(pady=(0, 6))                      # Espaciado vertical
        return e

    def _build(self):
        """
        Construye todos los widgets de la ventana:
        - Logo (si existe).
        - Campos email y contraseña.
        - Checkbutton para mostrar/ocultar contraseña.
        - Botón Ingresar.
        - Enlace a ventana de registro.
        """
        # Contenedor principal con fondo gris
        frm = tk.Frame(self.win, bg=COLOR_FONDO_GRIS)
        frm.pack(pady=20)  # Margen superior e inferior

        # -------------------------------
        # 1) Logo de la aplicación
        # -------------------------------
        try:
            from PIL import Image, ImageTk
            # Carga y redimensiona la imagen a 130x130
            img = Image.open("assets/klarity_logo.png").resize((130, 130))
            photo = ImageTk.PhotoImage(img)
            # Label que muestra la imagen
            tk.Label(frm, image=photo, bg=COLOR_FONDO_GRIS).pack()
            frm.image = photo  # Referencia para evitar garbage collector
        except Exception:
            # Si falla (archivo no existe), no mostramos logo pero continuamos
            pass

        # -------------------------------
        # 2) Campos de entrada
        # -------------------------------
        # Email:
        self.email = self._entry(frm, "Email:")
        # Contraseña (oculta por defecto con show="*"):
        self.password = self._entry(frm, "Contraseña:", show="*")

        # -------------------------------
        # 3) Mostrar/Ocultar contraseña
        # -------------------------------
        var_show = tk.BooleanVar(value=False)
        tk.Checkbutton(frm,
                       text="Mostrar contraseña",
                       bg=COLOR_FONDO_GRIS,
                       variable=var_show,
                       command=lambda: _toggle(self.password, var_show),
                       fg=COLOR_TEXTO_GRIS,
                       font=FONT_NORMAL
                       ).pack(anchor="w")

        # -------------------------------
        # 4) Botón Ingresar
        # -------------------------------
        tk.Button(frm,
                  text="Ingresar",
                  bg=COLOR_VERDE_CRECIMIENTO,
                  fg=COLOR_BLANCO,
                  font=FONT_NORMAL,
                  relief="flat",
                  command=self._login  # Llama a la función _login al pulsar
                  ).pack(pady=12)

        # -------------------------------
        # 5) Enlace para crear cuenta
        # -------------------------------
        link = tk.Label(frm,
                        text="Crear cuenta",
                        fg=COLOR_LINK_AZUL,
                        bg=COLOR_FONDO_GRIS,
                        cursor="hand2",  # Cursor en mano para simular enlace
                        font=FONT_NORMAL
                        )
        link.pack()
        # Al hacer clic, destruye esta ventana y crea la RegisterWindow
        link.bind("<Button-1>",
                  lambda e: [self.win.destroy(), RegisterWindow(self.root)]
                  )

    def _login(self):
        """
        Se ejecuta al pulsar 'Ingresar':
        - Toma email y contraseña del usuario.
        - Valida que no estén vacíos.
        - Llama a fb.login_user para autenticación.
        - Si OK: crea categorías por defecto, destruye ventana y abre Dashboard.
        - Si error: muestra un messagebox con el mensaje amigable.
        """
        email = self.email.get().strip()
        pwd = self.password.get().strip()

        # 1) Validación básica: campos obligatorios
        if not email or not pwd:
            messagebox.showerror("Error", "Completa los campos", parent=self.win)
            return

        # 2) Intento de login con Firebase
        user, err = fb.login_user(email, pwd)
        if err:
            # err ya es un mensaje traducido al español
            messagebox.showerror("Inicio de sesión fallido", err, parent=self.win)
            return

        # 3) Si es exitoso, nos aseguramos de que existan categorías por defecto
        fb.ensure_default_categories(user["localId"])

        # 4) Cerramos ventana de login y abrimos dashboard
        self.win.destroy()
        dashboard.DashboardWindow(self.root, user)


# ===========================================================================================
# Clase RegisterWindow
# -------------------------------------------------------------------------------------------
# Ventana para crear una cuenta nueva:
# - Campos: Nombre completo, Email, Contraseña, Confirmar contraseña.
# - Mostrar/ocultar contraseñas.
# - Botón Registrar y enlace para volver al login.
# ===========================================================================================

class RegisterWindow:
    def __init__(self, root: tk.Tk):
        """
        - root: referencia a la ventana raíz oculta.
        Crea una Toplevel, la configura y llama a _build.
        """
        self.root = root
        self.win = tk.Toplevel(root)
        self.win.title("Klarity – Registro")
        self.win.configure(bg=COLOR_FONDO_GRIS)
        center_window(self.win, 400, 700)  # Centra 400x700px (más alto para formularios)
        self._build()
        # Al cerrar con la 'X', destruye root y sale de la app.
        self.win.protocol("WM_DELETE_WINDOW", root.destroy)

    def _entry(self, parent, text: str, show: str = "") -> tk.Entry:
        """
        Reutiliza la misma lógica de LoginWindow para crear Label+Entry.
        """
        tk.Label(parent,
                 text=text,
                 bg=COLOR_FONDO_GRIS,
                 fg=COLOR_TEXTO_GRIS,
                 font=FONT_NORMAL
                 ).pack(anchor="w")
        e = tk.Entry(parent,
                     width=34,
                     font=FONT_NORMAL,
                     show=show,
                     relief="flat",
                     highlightbackground=COLOR_TEXTO_GRIS,
                     highlightthickness=1
                     )
        e.pack(pady=(0, 6))
        return e

    def _build(self):
        """
        Construye los widgets de la ventana de registro:
        - Logo, campos de nombre/email/contraseñas,
        - Mostrar/ocultar contraseñas,
        - Botón Registrar y enlace a login.
        """
        frm = tk.Frame(self.win, bg=COLOR_FONDO_GRIS)
        frm.pack(pady=15)

        # -------------------------------
        # Logo de Klarity (igual que en login)
        # -------------------------------
        try:
            from PIL import Image, ImageTk
            img = Image.open("assets/klarity_logo.png").resize((130, 130))
            photo = ImageTk.PhotoImage(img)
            tk.Label(frm, image=photo, bg=COLOR_FONDO_GRIS).pack()
            frm.image = photo
        except Exception:
            pass

        # -------------------------------
        # Campos de formulario
        # -------------------------------
        self.nombre = self._entry(frm, "Nombre completo:")
        self.email = self._entry(frm, "Email:")
        self.pwd1 = self._entry(frm, "Contraseña:", show="*")
        self.pwd2 = self._entry(frm, "Confirmar contraseña:", show="*")

        # -------------------------------
        # Mostrar/ocultar las dos contraseñas
        # -------------------------------
        var_show = tk.BooleanVar(value=False)
        tk.Checkbutton(frm,
                       text="Mostrar contraseñas",
                       bg=COLOR_FONDO_GRIS,
                       variable=var_show,
                       command=lambda: [_toggle(self.pwd1, var_show),
                                        _toggle(self.pwd2, var_show)],
                       fg=COLOR_TEXTO_GRIS,
                       font=FONT_NORMAL
                       ).pack(anchor="w")

        # -------------------------------
        # Botón Registrar
        # -------------------------------
        tk.Button(frm,
                  text="Registrar",
                  bg=COLOR_VERDE_CRECIMIENTO,
                  fg=COLOR_BLANCO,
                  font=FONT_NORMAL,
                  relief="flat",
                  command=self._register  # Llama a la lógica de registro
                  ).pack(pady=12)

        # -------------------------------
        # Enlace volver a login
        # -------------------------------
        back = tk.Label(frm,
                        text="Volver a inicio de sesión",
                        fg=COLOR_LINK_AZUL,
                        bg=COLOR_FONDO_GRIS,
                        cursor="hand2",
                        font=FONT_NORMAL
                        )
        back.pack()
        back.bind("<Button-1>",
                  lambda e: [self.win.destroy(), LoginWindow(self.root)]
                  )

    def _register(self):
        """
        Lógica de registro:
        1. Valida campos no vacíos.
        2. Verifica que contraseñas coincidan y tengan al menos 6 caracteres.
        3. Llama a fb.register_user.
        4. Si OK, crea perfil con nombre/email y categorías por defecto.
        5. Muestra mensaje y vuelve a login.
        """
        nom = self.nombre.get().strip()
        email = self.email.get().strip()
        p1 = self.pwd1.get().strip()
        p2 = self.pwd2.get().strip()

        # Validaciones básicas
        if not all([nom, email, p1, p2]):
            messagebox.showerror("Error", "Todos los campos son obligatorios.", parent=self.win)
            return
        if p1 != p2:
            messagebox.showerror("Error", "Contraseñas no coinciden.", parent=self.win)
            return
        if len(p1) < 6:
            messagebox.showerror("Error", "La contraseña debe tener al menos 6 caracteres.", parent=self.win)
            return

        # Registro en Firebase Auth
        user, err = fb.register_user(email, p1)
        if err:
            # Error (email existente, formato inválido, etc.)
            messagebox.showerror("Error", err, parent=self.win)
            return

        # 1) Creamos perfil con nombre y email
        fb.create_or_update_profile(
            user["localId"],
            {"nombre": nom, "email": email}
        )
        # 2) Aseguramos categorías por defecto
        fb.ensure_default_categories(user["localId"])

        # Informamos al usuario y lo enviamos al login
        messagebox.showinfo("Listo", "Cuenta creada, inicia sesión", parent=self.win)
        self.win.destroy() 
        LoginWindow(self.root)

# ===========================================================================================
# Función de utilidad: start()
# -------------------------------------------------------------------------------------------
# Permite iniciar el flujo de login desde fuera de este módulo:
# ui_login.start(root) creará la ventana de login.
# ===========================================================================================

def start(root: tk.Tk):
    LoginWindow(root)
