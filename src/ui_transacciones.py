# ===========================================================================================
# ui_transacciones.py
# -------------------------------------------------------------------------------------------
# Módulo encargado de:
# - Mostrar el historial de transacciones del usuario en una tabla.
# - Filtrar por periodo y rangos de fecha.
# - Ordenar dinámicamente por cualquier columna.
# - Agregar, editar y eliminar transacciones mediante modales.
# ===========================================================================================

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
from tkcalendar import DateEntry

from constants import *           # Colores, fuentes, constantes visuales
from utils import clear_frame, money  # Funciones reutilizables
import firebase_service as fb     # Lógica CRUD de transacciones en Firebase


def build(frame: tk.Frame, user: dict):
    """
    Construye la vista de Transacciones dentro del contenedor 'frame'.
    - frame: contenedor donde se renderiza la UI.
    - user: diccionario con datos del usuario (user['localId']).
    """

    # 1) Limpiar contenido previo
    clear_frame(frame)
    uid = user["localId"]

    # ─────────────────────────────────────────────────────────────────────
    # 2) Determinar fechas mín. y máx. de las transacciones reales
    #    para restringir selectores de fecha.
    # ─────────────────────────────────────────────────────────────────────

    data_all, _ = fb.get_transactions(uid)  # Traemos todas las transacciones
    fechas = []
    for v in (data_all or {}).values():
        try:
            # Convertimos timestamp a date
            fechas.append(datetime.fromtimestamp(v["fecha"]).date())
        except Exception:
            # Si el registro no tiene 'fecha' o es inválido, lo ignoramos
            pass

    if fechas:
        min_date = min(fechas)
        max_date = max(fechas)
    else:
        # Si no hay transacciones, usamos rango por defecto (últimos 30 días)
        max_date = date.today()
        min_date = max_date - timedelta(days=30)

    # ─────────────────────────────────────────────────────────────────────
    # 3) Variables para ordenar dinámicamente la tabla
    # ─────────────────────────────────────────────────────────────────────

    sort_col     = "Fecha"   # Columna activa para ordenar
    sort_reverse = False     # Dirección de orden (asc/desc)
    # Mapea nombres de encabezado a campos en los datos
    col_map = {
        "Fecha":        "fecha",
        "Descripción":  "descripcion",
        "Monto":        "monto",
        "Tipo":         "tipo",
        "Categoría":    "categoria",
    }

    # ─────────────────────────────────────────────────────────────────────
    # 4) Estilos para la tabla y botones usando ttk.Style
    # ─────────────────────────────────────────────────────────────────────

    style = ttk.Style()
    style.theme_use("clam")  # Tema visual "clam"
    # Configuramos estilo general de filas
    style.configure("Treeview",
                    rowheight=24,
                    font=FONT_NORMAL)
    style.map("Treeview",
              background=[("selected", COLOR_VERDE_CRECIMIENTO)],
              foreground=[("selected", COLOR_BLANCO)])
    # Estilo de encabezados
    style.configure("Treeview.Heading",
                    background=COLOR_PRINCIPAL_AZUL,
                    foreground=COLOR_BLANCO,
                    font=("Lato", 11, "bold"))
    # Botones de acción (Accent y Danger)
    style.configure("Accent.TButton",
                    background=COLOR_VERDE_CRECIMIENTO,
                    foreground=COLOR_BLANCO,
                    font=FONT_NORMAL,
                    padding=(8,4))
    style.map("Accent.TButton",
              background=[("active", COLOR_VERDE_CRECIMIENTO)])
    style.configure("Danger.TButton",
                    background=COLOR_ROJO_GASTO,
                    foreground=COLOR_BLANCO,
                    font=FONT_NORMAL,
                    padding=(8,4))
    style.map("Danger.TButton",
              background=[("active", COLOR_ROJO_GASTO)])

    # ─────────────────────────────────────────────────────────────────────
    # 5) Toolbar superior: título y botones de Nuevo/Editar/Eliminar
    # ─────────────────────────────────────────────────────────────────────

    top = tk.Frame(frame, bg=COLOR_FONDO_GRIS)
    top.pack(fill="x", pady=(0,6), padx=10)
    top.columnconfigure(0, weight=1)  # Columna 0 ocupa todo el espacio
    top.columnconfigure(1, weight=0)

    # Título
    tk.Label(top,
             text="Historial de Movimientos",
             font=FONT_TITLE,
             bg=COLOR_FONDO_GRIS,
             fg=COLOR_PRINCIPAL_AZUL
             ).grid(row=0, column=0, sticky="w")

    # Contenedor de botones
    acciones = tk.Frame(top, bg=COLOR_FONDO_GRIS)
    acciones.grid(row=0, column=1, sticky="e")
    btn_editar = ttk.Button(acciones, text="✏️ Editar",   style="Accent.TButton")
    btn_borrar = ttk.Button(acciones, text="🗑️ Eliminar", style="Danger.TButton")
    btn_nuevo  = ttk.Button(acciones, text="+ Nuevo",     style="Accent.TButton")
    btn_editar.grid (row=0, column=0, padx=4)
    btn_borrar.grid (row=0, column=1, padx=4)
    btn_nuevo .grid (row=0, column=2, padx=4)

    # Línea divisoria
    ttk.Separator(frame, orient="horizontal")\
        .pack(fill="x", padx=10, pady=(0,6))

    # ─────────────────────────────────────────────────────────────────────
    # 6) Filtro de fechas / periodos rápidos
    # ─────────────────────────────────────────────────────────────────────

    filtro = tk.Frame(frame, bg=COLOR_FONDO_GRIS)
    filtro.pack(fill="x", padx=10, pady=(0,6))

    # Label “Periodo”
    tk.Label(filtro,
             text="Periodo:",
             bg=COLOR_FONDO_GRIS,
             fg=COLOR_TEXTO_GRIS
             ).pack(side="left")

    # Opciones de periodo rápido
    periodos = ["Personalizado","Hoy","Ayer","Últimos 7 días",
                "Últimos 30 días","Este Mes","Este Año"]
    period_var = tk.StringVar(value="Personalizado")
    cb_period = ttk.Combobox(filtro,
                             values=periodos,
                             state="readonly",
                             width=14,
                             textvariable=period_var)
    cb_period.pack(side="left", padx=(4,12))

    # DateEntry “Desde”
    tk.Label(filtro,
             text="Desde:",
             bg=COLOR_FONDO_GRIS,
             fg=COLOR_TEXTO_GRIS
             ).pack(side="left")
    date_from = DateEntry(filtro,
                          date_pattern="yyyy-mm-dd",
                          mindate=min_date,
                          maxdate=None)
    date_from.pack(side="left", padx=(4,12))
    date_from.set_date(min_date)

    # DateEntry “Hasta”
    tk.Label(filtro,
             text="Hasta:",
             bg=COLOR_FONDO_GRIS,
             fg=COLOR_TEXTO_GRIS
             ).pack(side="left")
    date_to = DateEntry(filtro,
                        date_pattern="yyyy-mm-dd",
                        mindate=min_date,
                        maxdate=None)
    date_to.pack(side="left", padx=(4,12))
    date_to.set_date(max_date)

    # Botones aplicar y mostrar todos
    btn_apply = ttk.Button(filtro,
                           text="Aplicar filtro",
                           style="Accent.TButton")
    btn_apply.pack(side="left", padx=4)
    btn_all   = ttk.Button(filtro,
                           text="Mostrar todos",
                           style="Accent.TButton")
    btn_all.pack(side="left", padx=4)

    # ─────────────────────────────────────────────────────────────────────
    # 7) Tabla con encabezados clicables y zebra-striping
    # ─────────────────────────────────────────────────────────────────────

    cols = ("Fecha","Descripción","Monto","Tipo","Categoría")
    tree = ttk.Treeview(frame,
                        columns=cols,
                        show="headings",
                        height=15)
    # Configuramos cada encabezado para ordenar llamando a sort_by_column
    for c in cols:
        tree.heading(c,
                     text=c,
                     command=lambda _c=c: sort_by_column(_c))
        tree.column(c, anchor="center", stretch=True)
    tree.pack(fill="both", expand=True, padx=10, pady=(0,10))

    # Zebra-striping: filas alternas claro/oscuro
    def tag_rows():
        for i, iid in enumerate(tree.get_children()):
            tree.item(iid, tags=("odd",) if i%2 else ("even",))
    tree.tag_configure("odd",  background="#f0f4f7")
    tree.tag_configure("even", background="#e7edf1")

    # ─────────────────────────────────────────────────────────────────────
    # 8) Funciones internas: orden, carga, filtros y modales
    # ─────────────────────────────────────────────────────────────────────

    def sort_by_column(col):
        """
        Ordena la tabla por la columna 'col':
        - Alterna asc/desc si se vuelve a clicar en el mismo.
        - Resetea dirección si cambia de columna.
        """
        nonlocal sort_col, sort_reverse
        if sort_col == col:
            sort_reverse = not sort_reverse
        else:
            sort_col     = col
            sort_reverse = False
        cargar()  # Refresca la tabla con el nuevo orden

    def cargar():
        """
        Recupera transacciones de Firebase, aplica filtros de fecha
        y orden, luego inserta filas en el Treeview.
        """
        tree.delete(*tree.get_children())
        data, _ = fb.get_transactions(uid)
        # Convertimos dict a lista de registros con clave
        lista = [{"__key":k, **v} for k,v in (data or {}).items()]

        # Filtrar según fechas seleccionadas
        d0 = date_from.get_date()
        d1 = date_to.get_date()
        lista = [t for t in lista
                 if d0 <= datetime.fromtimestamp(t["fecha"]).date() <= d1]

        # Ordenar según encabezado
        key = col_map[sort_col]
        if key in ("fecha","monto"):
            lista.sort(key=lambda t: t.get(key,0), reverse=sort_reverse)
        else:
            lista.sort(key=lambda t: t.get(key,"").lower(), reverse=sort_reverse)

        # Insertar filas en el Treeview
        for t in lista:
            tree.insert("", "end", iid=t["__key"], values=(
                datetime.fromtimestamp(t["fecha"]).strftime("%Y-%m-%d"),
                t.get("descripcion",""),
                money(t.get("monto",0)),  # Formatea con separadores COP
                t.get("tipo",""),
                t.get("categoria","—")
            ))
        tag_rows()

    # Asignamos funciones a botones de filtro
    btn_apply.configure(command=cargar)

    def mostrar_todos():
        """Resetea DateEntry al rango completo y recarga."""
        date_from.set_date(min_date)
        date_to.set_date(max_date)
        cargar()
    btn_all.configure(command=mostrar_todos)

    # Gestión de selección de periodos rápidos
    def on_period_change(*_):
        p = period_var.get()
        hoy = date.today()
        # Rehabilita DateEntry para luego deshabilitar si no es personalizado
        date_from.config(state="normal")
        date_to.config(state="normal")

        if p=="Hoy":
            d0 = d1 = hoy
        elif p=="Ayer":
            d0 = d1 = hoy - timedelta(days=1)
        elif p=="Últimos 7 días":
            d0 = hoy - timedelta(days=6); d1 = hoy
        elif p=="Últimos 30 días":
            d0 = hoy - timedelta(days=29); d1 = hoy
        elif p=="Este Mes":
            d0 = hoy.replace(day=1); d1 = hoy
        elif p=="Este Año":
            d0 = hoy.replace(month=1, day=1); d1 = hoy
        else:
            return  # personalizado

        # Clamp fechas al rango disponible
        if d0 < min_date: d0 = min_date
        if d1 > date.today(): d1 = date.today()

        date_from.set_date(d0)
        date_to.set_date(d1)
        # Deshabilita entradas si no es periodo personalizado
        if p!="Personalizado":
            date_from.config(state="disabled")
            date_to.config(state="disabled")
        cargar()

    period_var.trace_add("write", on_period_change)

    # ─────────────────────────────────────────────────────────────────────
    # 9) Modal para agregar/editar transacción
    # ─────────────────────────────────────────────────────────────────────

    def modal_edit(key=None, data=None):
        """
        Abre un Toplevel con campos para crear o editar:
        - key: si se pasa, editamos esa transacción.
        - data: dict con valores prellenados (solo en edición).
        """
        is_edit = key is not None
        m = tk.Toplevel(frame)
        m.title("Editar Movimiento" if is_edit else "Nuevo Movimiento")
        m.grab_set()           # Modal: bloquea interacción con la ventana padre
        m.configure(bg=COLOR_FONDO_GRIS)

        # Layout con grid: etiquetas y entradas
        lab = dict(sticky="e", padx=5, pady=4)
        ent = dict(padx=5, pady=4)

        tk.Label(m, text="Descripción:", bg=COLOR_FONDO_GRIS).grid(row=0, column=0, **lab)
        desc = tk.Entry(m, width=30); desc.grid(row=0, column=1, **ent)

        tk.Label(m, text="Monto:", bg=COLOR_FONDO_GRIS).grid(row=1, column=0, **lab)
        em = tk.Entry(m, width=30); em.grid(row=1, column=1, **ent)

        tk.Label(m, text="Fecha:", bg=COLOR_FONDO_GRIS).grid(row=2, column=0, **lab)
        fp = DateEntry(m, date_pattern="yyyy-mm-dd")
        fp.grid(row=2, column=1, **ent)

        # ComboBox de categorías existentes
        cats_dict, _ = fb.get_categories(uid)
        names = [c["nombre"] for c in cats_dict.values()] if cats_dict else ["—"]
        tk.Label(m, text="Categoría:", bg=COLOR_FONDO_GRIS).grid(row=3, column=0, **lab)
        cb = ttk.Combobox(m, values=names, state="readonly"); cb.grid(row=3, column=1, **ent)
        cb.current(0)

        # Radio buttons para tipo Ingreso/Gasto
        tv = tk.StringVar(value="Gasto")
        ttk.Radiobutton(m, text="Ingreso", variable=tv, value="Ingreso")\
            .grid(row=4, column=0, pady=4)
        ttk.Radiobutton(m, text="Gasto",   variable=tv, value="Gasto")\
            .grid(row=4, column=1, pady=4)

        # Si es edición, prellenar campos
        if is_edit and data:
            desc.insert(0, data.get("descripcion",""))
            em.insert(0, str(data.get("monto","")))
            fp.set_date(datetime.fromtimestamp(data["fecha"]))
            cb.set(data.get("categoria","—"))
            tv.set(data.get("tipo","Gasto"))

        # Función guardar: valida y crea/actualiza en Firebase
        def guardar():
            try:
                mv = float(em.get())
            except ValueError:
                messagebox.showerror("Error", "Monto inválido", parent=m)
                return
            payload = {
                "descripcion": desc.get(),
                "monto": mv,
                "categoria": cb.get(),
                "tipo": tv.get(),
                # Convertimos fecha a timestamp en segundos
                "fecha": datetime.combine(fp.get_date(), datetime.min.time()).timestamp()
            }
            if is_edit:
                ok, err = fb.update_transaction(uid, key, payload)
            else:
                _, err = fb.add_transaction(uid, payload)
                ok = (err is None)
            if err or not ok:
                messagebox.showerror("Error", err or "Error desconocido", parent=m)
                return
            m.destroy()
            cargar()

        # Botón Guardar
        ttk.Button(m,
                   text="Guardar",
                   style="Accent.TButton",
                   command=guardar
                   ).grid(row=5, columnspan=2, pady=(10,8))

    # Enlazamos botones de CRUD con sus funciones
    btn_nuevo .configure(command=lambda: modal_edit())
    btn_borrar.configure(command=lambda: (
        messagebox.askyesno("Confirmar", "¿Eliminar movimiento?", parent=frame)
        and fb.delete_transaction(uid, tree.selection()[0])
        and cargar()
    ))
    btn_editar.configure(command=lambda: (
        tree.selection() and
        fb.get_single_transaction(uid, tree.selection()[0])[0] and
        modal_edit(tree.selection()[0],
                   fb.get_single_transaction(uid, tree.selection()[0])[0])
    ))

    # ─────────────────────────────────────────────────────────────────────
    # 10) Inicializar: mostramos todos al cargar la sección por primera vez
    # ─────────────────────────────────────────────────────────────────────

    mostrar_todos()
