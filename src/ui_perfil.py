# ===========================================================================================
# ui_perfil.py
# -------------------------------------------------------------------------------------------
# Módulo para la vista de Perfil de usuario:
# - Mostrar y actualizar nombre y foto de perfil.
# - Seleccionar nueva imagen desde el sistema de archivos.
# - Cambiar contraseña (re-autenticación + actualización).
# ===========================================================================================

import os
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw  # Pillow para manipulación de imágenes

from constants import *       # Colores, fuentes, constantes globales
from utils import clear_frame  # Función para vaciar el contenedor antes de renderizar
import firebase_service as fb  # Funciones CRUD en Firebase

def build(frame: tk.Frame, user: dict):
    """
    Construye la interfaz de Perfil dentro de 'frame':
    - Carga datos actuales del perfil desde Firebase.
    - Muestra foto circular, nombre y formularios.
    - Permite cambiar foto, nombre y contraseña.
    """

    # 1) Limpiamos el contenedor para renderizar desde cero
    clear_frame(frame)
    uid = user["localId"]     # UID actual de Firebase
    email = user.get("email", "")

    # 2) Recuperar perfil desde Realtime Database
    perfil, err = fb.get_profile(uid)
    if err:
        # Si hay error, mostramos alerta y usamos datos en blanco
        messagebox.showerror("Error", f"No se pudo cargar perfil:\n{err}", parent=frame)
        perfil = {}

    # 3) Contenedor principal con margen interior
    container = tk.Frame(frame, bg=COLOR_FONDO_GRIS)
    container.pack(fill="both", expand=True, padx=30, pady=30)

    # ──────────────────────────────────────────────────────────────────────────
    # 4) Título “Mi Perfil”
    # ──────────────────────────────────────────────────────────────────────────
    tk.Label(
        container,
        text="Mi Perfil",
        font=FONT_TITLE,
        bg=COLOR_FONDO_GRIS,
        fg=COLOR_PRINCIPAL_AZUL
    ).pack(pady=(0,20))

    # ──────────────────────────────────────────────────────────────────────────
    # 5) Avatar circular de perfil
    # ──────────────────────────────────────────────────────────────────────────
    avatar_path = perfil.get("foto", "")  # Ruta almacenada en DB
    avatar_img = None

    if avatar_path:
        try:
            # Abrir imagen y convertir a RGBA para manejar transparencia
            img = Image.open(avatar_path).convert("RGBA")
            # Redimensionar a 150x150 píxeles
            img = img.resize((150,150), resample=Image.LANCZOS)

            # Crear máscara circular
            mask = Image.new("L", (150,150), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0,0,150,150), fill=255)
            img.putalpha(mask)  # Aplicar la máscara

            # Convertir a PhotoImage para Tkinter
            avatar_img = ImageTk.PhotoImage(img)
        except Exception:
            avatar_img = None  # Si hay fallo, ignoramos la imagen

    # Label para mostrar avatar (puede quedar vacío si no hay imagen)
    lbl_avatar = tk.Label(container, image=avatar_img, bg=COLOR_FONDO_GRIS)
    lbl_avatar.image = avatar_img  # Referencia para evitar recolección de basura
    lbl_avatar.pack(pady=(0,10))

    # ──────────────────────────────────────────────────────────────────────────
    # 6) Botón “Cambiar foto”: abre diálogo y actualiza preview
    # ──────────────────────────────────────────────────────────────────────────
    foto_var = tk.StringVar(value=avatar_path)  # Variable que almacena ruta actual

    def sel_foto():
        """
        Abre un cuadro de diálogo para seleccionar archivo.
        - Actualiza foto_var y preview circular.
        """
        p = filedialog.askopenfilename(
            filetypes=[("Imágenes","*.png *.jpg *.jpeg")]
        )
        if not p:
            return  # Si el usuario cancela, no hacemos nada

        foto_var.set(p)  # Guardar nueva ruta

        try:
            # Mismo proceso de máscara circular para preview
            img2 = Image.open(p).convert("RGBA")
            img2 = img2.resize((150,150), resample=Image.LANCZOS)
            mask2 = Image.new("L", (150,150), 0)
            draw2 = ImageDraw.Draw(mask2)
            draw2.ellipse((0,0,150,150), fill=255)
            img2.putalpha(mask2)
            tk2 = ImageTk.PhotoImage(img2)
            lbl_avatar.configure(image=tk2)
            lbl_avatar.image = tk2
        except Exception:
            pass  # Si falla preview, la imagen anterior permanece

    tk.Button(
        container,
        text="Cambiar foto",
        bg=COLOR_PRINCIPAL_AZUL,
        fg=COLOR_BLANCO,
        relief="flat",
        command=sel_foto
    ).pack(pady=(0,20))

    # ──────────────────────────────────────────────────────────────────────────
    # 7) Formulario para editar nombre completo
    # ──────────────────────────────────────────────────────────────────────────
    frm = tk.Frame(container, bg=COLOR_FONDO_GRIS)
    frm.pack(pady=(0,20))

    tk.Label(frm, text="Nombre completo:", bg=COLOR_FONDO_GRIS).grid(
        row=0, column=0, sticky="e", padx=5
    )
    entry_nombre = tk.Entry(frm, width=30)
    entry_nombre.grid(row=0, column=1, padx=5)
    entry_nombre.insert(0, perfil.get("nombre",""))  # Valor inicial

    # Función para actualizar nombre y foto en Firebase
    def guardar_datos():
        nuevo = entry_nombre.get().strip()
        if not nuevo:
            messagebox.showwarning(
                "Atención",
                "El nombre no puede quedar vacío.",
                parent=container
            )
            return

        datos = {
            "nombre": nuevo,
            "foto": foto_var.get()
        }
        ok, e = fb.create_or_update_profile(uid, datos)
        if not ok:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}", parent=container)
            return

        messagebox.showinfo("Éxito", "Perfil actualizado.", parent=container)

    tk.Button(
        container,
        text="Guardar cambios",
        bg=COLOR_VERDE_CRECIMIENTO,
        fg=COLOR_BLANCO,
        relief="flat",
        command=guardar_datos
    ).pack(pady=(0,10))

    # ──────────────────────────────────────────────────────────────────────────
    # 8) Sección “Seguridad”: cambiar contraseña
    # ──────────────────────────────────────────────────────────────────────────
    sec = tk.Frame(container, bg="white", bd=1, relief='solid')
    sec.pack(fill='x', pady=20)

    # Título sección
    tk.Label(sec, text="Seguridad", font=FONT_NORMAL, bg="white").pack(fill='x', pady=(10,0))

    form2 = tk.Frame(sec, bg="white")
    form2.pack(padx=20, pady=10)

    # Campos: contraseña actual, nueva y confirmación
    tk.Label(form2, text="Contraseña actual:", bg="white").grid(row=0, column=0, sticky="e", pady=5)
    entry_old = tk.Entry(form2, show="*", width=30)
    entry_old.grid(row=0, column=1, pady=5)

    tk.Label(form2, text="Nueva contraseña:", bg="white").grid(row=1, column=0, sticky="e", pady=5)
    entry_new = tk.Entry(form2, show="*", width=30)
    entry_new.grid(row=1, column=1, pady=5)

    tk.Label(form2, text="Confirmar contraseña:", bg="white").grid(row=2, column=0, sticky="e", pady=5)
    entry_conf = tk.Entry(form2, show="*", width=30)
    entry_conf.grid(row=2, column=1, pady=5)

    # Checkbutton para mostrar/ocultar texto de contraseña
    show_var = tk.BooleanVar(value=False)
    def toggle_show():
        s = '' if show_var.get() else '*'
        entry_old.config(show=s)
        entry_new.config(show=s)
        entry_conf.config(show=s)

    chk = tk.Checkbutton(
        sec,
        text="Mostrar contraseña",
        bg="white",
        variable=show_var,
        command=toggle_show
    )
    chk.pack(pady=(0,10))

    # Lógica para cambiar contraseña
    def cambiar_password():
        old  = entry_old.get().strip()
        new  = entry_new.get().strip()
        conf = entry_conf.get().strip()

        # Validaciones básicas
        if not (old and new and conf):
            messagebox.showwarning("Atención", "Complete todos los campos.", parent=sec)
            return
        if new != conf:
            messagebox.showwarning("Atención", "La nueva contraseña y su confirmación no coinciden.", parent=sec)
            return

        # 1) Re-autenticación con la contraseña actual
        ok, err = fb.reauthenticate_user(email, old)
        if not ok:
            messagebox.showerror("Error", "Contraseña actual incorrecta.", parent=sec)
            return

        # 2) Actualizar contraseña via Admin SDK
        ok2, err2 = fb.update_password(uid, new)
        if not ok2:
            messagebox.showerror("Error", f"No se pudo cambiar la contraseña:\n{err2}", parent=sec)
            return

        # 3) Éxito: notificamos y limpiamos campos
        messagebox.showinfo("Éxito", "Contraseña actualizada correctamente.", parent=sec)
        entry_old.delete(0, 'end')
        entry_new.delete(0, 'end')
        entry_conf.delete(0, 'end')
        show_var.set(False)
        toggle_show()

    tk.Button(
        sec,
        text="Cambiar contraseña",
        bg=COLOR_VERDE_CRECIMIENTO,
        fg=COLOR_BLANCO,
        font=FONT_NORMAL,
        relief="flat",
        command=cambiar_password
    ).pack(pady=(0,10))

    # Evitar que el container se redimensione según contenido
    container.pack_propagate(False)
