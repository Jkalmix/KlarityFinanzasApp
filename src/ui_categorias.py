# =====================================================================================
# ui_categorias.py
# -------------------------------------------------------------------------------------
# Módulo responsable de:
# - Mostrar y gestionar (CRUD) las categorías de ingresos/gastos del usuario.
# - Pantalla con tabla, ordenamiento, estilo “zebra” y encabezados clicables.
# - Modales para crear y editar con validaciones.
# - Confirmación al eliminar.
# =====================================================================================

import tkinter as tk
from tkinter import ttk, messagebox

from constants import *      # Colores, fuentes y constantes visuales
from utils import clear_frame  # Función para limpiar el contenedor
import firebase_service as fb  # Lógica CRUD en Firebase para categorías


def build(frame: tk.Frame, user: dict):
    """
    Construye la UI de Categorías en el contenedor 'frame'.
    - frame: donde se renderiza la vista.
    - user: dict con datos del usuario (user['localId']).
    """

    # 1) Limpiamos cualquier widget previo en el contenedor
    clear_frame(frame)
    uid = user['localId']  # UID de Firebase para scoping de datos

    # ────────────────────────────────────────────────────────────────
    # 2) Toolbar superior: título y botones de acción
    # ────────────────────────────────────────────────────────────────

    toolbar = tk.Frame(frame, bg=COLOR_FONDO_GRIS, padx=10, pady=6)
    toolbar.pack(fill="x")

    # Título centrado a la izquierda
    title = tk.Label(
        toolbar,
        text="Categorías",
        font=("Lato", 28, "bold"),
        bg=COLOR_FONDO_GRIS,
        fg=COLOR_PRINCIPAL_AZUL
    )
    title.pack(side="left")

    # ────────────────────────────────────────────────────────────────
    # 3) Contenedor de la tabla de categorías
    # ────────────────────────────────────────────────────────────────

    container = tk.Frame(frame, bg=COLOR_FONDO_GRIS, padx=20, pady=10)
    container.pack(fill="both", expand=True)

    # Definimos columnas: Nombre y Tipo
    cols = ("Nombre", "Tipo")
    tree = ttk.Treeview(container, columns=cols, show="headings")

    # ────────────────────────────────────────────────────────────────
    # 4) Estilos y zebra-striping para legibilidad
    # ────────────────────────────────────────────────────────────────

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", rowheight=30, font=FONT_NORMAL)
    style.map(
        "Treeview",
        background=[('selected', COLOR_VERDE_CRECIMIENTO)],
        foreground=[('selected', COLOR_BLANCO)]
    )
    # Definimos dos tags para filas alternas
    tree.tag_configure('odd',  background='#FAFAFA')
    tree.tag_configure('even', background='#FFFFFF')

    # Diccionario para llevar el estado de orden de cada columna
    sort_reverse = {c: False for c in cols}


    # ────────────────────────────────────────────────────────────────
    # 5) Funciones auxiliares internas
    # ────────────────────────────────────────────────────────────────

    def tag_rows():
        """
        Asigna tags 'odd' y 'even' alternando filas
        para crear efecto zebra.
        """
        for i, iid in enumerate(tree.get_children()):
            tag = 'odd' if i % 2 else 'even'
            tree.item(iid, tags=(tag,))

    def cargar(items=None):
        """
        Carga las categorías desde Firebase y las inserta en la tabla.
        - items: lista pre-ordenada [(key, data), ...], si no se pasa,
          se obtienen y usan en orden original.
        """
        tree.delete(*tree.get_children())
        cats_dict, _ = fb.get_categories(uid)
        data_list = items if items is not None else list(cats_dict.items())

        # Si no hay categorías, mostramos fila indicativa
        if not data_list:
            tree.insert('', 'end', values=('No hay categorías', ''), tags=('even',))
            return

        # Insertamos cada categoría: key es ID, values son nombre y tipo
        for key, cat in data_list:
            tree.insert('', 'end', iid=key, values=(cat['nombre'], cat['tipo']))

        tag_rows()  # Aplicamos zebra-striping

    def sort_by(col):
        """
        Ordena las categorías por columna 'col' (Nombre o Tipo).
        Alterna ascendente/descendente según sort_reverse.
        """
        cats_dict, _ = fb.get_categories(uid)
        items = list(cats_dict.items())
        # Ordenamos usando la clave correspondiente en el diccionario
        items.sort(
            key=lambda x: x[1][col.lower()],
            reverse=sort_reverse[col]
        )
        sort_reverse[col] = not sort_reverse[col]
        cargar(items)  # Recargamos tabla con items ordenados

    def modal_cat(cat=None, key=None):
        """
        Abre un modal Toplevel para crear o editar una categoría.
        - cat: datos preexistentes (solo en edición).
        - key: ID en Firebase de la categoría (solo en edición).
        """
        is_edit = key is not None
        m = tk.Toplevel(frame)
        m.title("Editar Categoría" if is_edit else "Nueva Categoría")
        m.configure(bg=COLOR_FONDO_GRIS)
        m.grab_set()  # Modal: bloquea la ventana padre

        # Campo Nombre
        tk.Label(m, text="Nombre:", bg=COLOR_FONDO_GRIS)\
            .grid(row=0, column=0, sticky="e", padx=5, pady=5)
        ent_name = tk.Entry(m, width=30)
        ent_name.grid(row=0, column=1, padx=5, pady=5)

        # Campo Tipo con Radiobuttons
        tk.Label(m, text="Tipo:", bg=COLOR_FONDO_GRIS)\
            .grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tipo_var = tk.StringVar(value="Gasto")
        ttk.Radiobutton(m, text="Ingreso", variable=tipo_var, value="Ingreso")\
            .grid(row=1, column=1, sticky="w")
        ttk.Radiobutton(m, text="Gasto", variable=tipo_var, value="Gasto")\
            .grid(row=1, column=1, sticky="e")

        # Si estamos editando, precargamos valores
        if is_edit and cat:
            ent_name.insert(0, cat['nombre'])
            tipo_var.set(cat['tipo'])

        def guardar():
            """
            Valida entradas y llama a Firebase:
            - add_category en creación.
            - update_category en edición.
            """
            nombre = ent_name.get().strip()
            if not nombre:
                messagebox.showwarning("Atención", "El nombre es obligatorio.", parent=m)
                return

            datos = {"nombre": nombre, "tipo": tipo_var.get()}
            if is_edit:
                ok, err = fb.update_category(uid, key, datos)
            else:
                _, err = fb.add_category(uid, datos)
                ok = (err is None)

            if err or not ok:
                messagebox.showerror("Error", err or "Error desconocido", parent=m)
                return

            m.destroy()
            cargar()  # Recargamos tabla tras guardar

        # Botón Guardar
        btn_save = tk.Button(
            m,
            text="Guardar",
            bg=COLOR_VERDE_CRECIMIENTO,
            fg=COLOR_BLANCO,
            relief="flat",
            padx=12,
            pady=6,
            command=guardar
        )
        btn_save.grid(row=2, columnspan=2, pady=10)

    def eliminar():
        """
        Borra la categoría seleccionada tras confirmar con el usuario.
        """
        sel = tree.selection()
        if not sel:
            return

        key = sel[0]
        if messagebox.askyesno(
            "Confirmar eliminación",
            "¿Seguro que deseas eliminar esta categoría?",
            parent=frame
        ):
            ok, err = fb.delete_category(uid, key)
            if err or not ok:
                messagebox.showerror("Error", err or "Error desconocido", parent=frame)
            cargar()  # Recarga tabla

    def modal_edit():
        """
        Recupera la categoría seleccionada y abre el modal de edición.
        """
        sel = tree.selection()
        if sel:
            cats_dict, _ = fb.get_categories(uid)
            key = sel[0]
            modal_cat(cat=cats_dict[key], key=key)


    # ────────────────────────────────────────────────────────────────
    # 6) Configuramos encabezados clicables para ordenar
    # ────────────────────────────────────────────────────────────────

    for col in cols:
        tree.heading(
            col,
            text=col,
            anchor="w",
            command=lambda _c=col: sort_by(_c)
        )

    tree.pack(fill="both", expand=True)

    # ────────────────────────────────────────────────────────────────
    # 7) Botones inferiores: Añadir, Editar, Eliminar
    # ────────────────────────────────────────────────────────────────

    btn_del = tk.Button(
        toolbar,
        text="🗑️ Eliminar",
        font=FONT_NORMAL,
        bg=COLOR_ROJO_GASTO,
        fg=COLOR_BLANCO,
        relief="flat",
        padx=12,
        pady=6,
        command=eliminar
    )
    btn_del.pack(side="right", padx=(5,0))

    btn_edit = tk.Button(
        toolbar,
        text="✎ Editar",
        font=FONT_NORMAL,
        bg=COLOR_PRINCIPAL_AZUL,
        fg=COLOR_BLANCO,
        relief="flat",
        padx=12,
        pady=6,
        command=modal_edit
    )
    btn_edit.pack(side="right", padx=5)

    btn_add = tk.Button(
        toolbar,
        text="+ Nueva",
        font=FONT_NORMAL,
        bg=COLOR_VERDE_CRECIMIENTO,
        fg=COLOR_BLANCO,
        relief="flat",
        padx=12,
        pady=6,
        command=lambda: modal_cat()
    )
    btn_add.pack(side="right", padx=(0,5))

    # ────────────────────────────────────────────────────────────────
    # 8) Carga inicial de datos
    # ────────────────────────────────────────────────────────────────

    cargar()
