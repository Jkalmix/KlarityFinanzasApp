# ===========================================================================================
# ui_dashboard.py
# -------------------------------------------------------------------------------------------
# Módulo principal de la interfaz tras iniciar sesión:
# - Crea la ventana de Dashboard (Toplevel).
# - Construye barra lateral de navegación.
# - Gestiona contenido dinámico: Home, Transacciones, Categorías, Reportes, Asistente AI, Perfil.
# - Permite cerrar sesión y volver al login.
# ===========================================================================================

import tkinter as tk                             # Widgets básicos
from tkinter import ttk                          # Widgets “themed” (combobox, treeview...)
from datetime import datetime, date, timedelta   # Para manejo de fechas
from tkcalendar import DateEntry                # Selector de fecha en GUI

from constants import *                          # Colores, fuentes y otros valores
from utils import clear_frame                    # Función para limpiar contenedores

# Importamos los módulos de cada sección para renderizar en el panel central
import firebase_service as fb
import ui_transacciones as trans
import ui_categorias as cats
import ui_reportes as reps
import ui_perfil as perfil
import ui_ai_advisor as advisor

import pandas as pd                              # Para DataFrame y manipulación de datos
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt                  # Para crear gráficos

import os                                        # Para comprobar existencia de archivos
from PIL import Image, ImageTk, ImageOps, ImageDraw
                                                # Para cargar y manipular imágenes

# ===========================================================================================
# Clase DashboardWindow
# -------------------------------------------------------------------------------------------
# Representa la ventana principal de la app después del login.
# Contiene:
# 1) Barra lateral con botones de navegación.
# 2) Panel central dinámico según la sección elegida.
# ===========================================================================================

class DashboardWindow:
    def __init__(self, root, user):
        """
        - root: ventana raíz oculta de Tkinter.
        - user: diccionario con datos del usuario autenticado (contiene 'email', 'localId', etc.).
        Crea un Toplevel, configura tamaño y colores, y llama a _build_ui.
        """
        self.root = root
        self.user = user
        # Creamos ventana de nivel superior
        self.win = tk.Toplevel(root)
        self.win.title("Klarity – Dashboard")
        self.win.geometry("1024x720")               # Tamaño inicial
        self.win.configure(bg=COLOR_FONDO_GRIS)
        self._build_ui()                            # Construye todos los elementos UI

    def _build_ui(self):
        """
        Genera la interfaz completa:
        - Barra lateral con logo y botones.
        - Contenedor principal donde cargan las secciones.
        - Configura evento de logout.
        """
        # -------------------------
        # 1) Barra lateral (Frame 'nav')
        # -------------------------
        nav = tk.Frame(self.win,
                       bg=COLOR_PRINCIPAL_AZUL,
                       width=220)                # Ancho fijo
        nav.pack(side="left", fill="y")            # Ocupa toda la altura
        nav.pack_propagate(False)                  # No ajusta su tamaño a los hijos

        # ------ Logo en la parte superior ------
        try:
            # Intentamos cargar logo desde assets/
            logo = Image.open("assets/klarity_logo.png")\
                        .resize((80, 80), Image.Resampling.LANCZOS)
            ph_logo = ImageTk.PhotoImage(logo)
            tk.Label(nav, image=ph_logo,
                     bg=COLOR_PRINCIPAL_AZUL).pack(pady=(18, 8))
            nav.logo = ph_logo  # Guardamos referencia para evitar GC
        except Exception:
            # Si no existe la imagen, mostramos texto en su lugar
            tk.Label(nav, text="Klarity",
                     font=("Lato", 24, "bold"),
                     fg=COLOR_BLANCO,
                     bg=COLOR_PRINCIPAL_AZUL
                     ).pack(pady=(22, 10))

        # -------------------------
        # 2) Botones de navegación
        # -------------------------
        # Definimos lista de tuplas (texto botón, función a ejecutar)
        items = [
            ("Dashboard",     self._home),
            ("Transacciones", lambda: trans.build(self.content, self.user)),
            ("Categorías",    lambda: cats.build(self.content, self.user)),
            ("Reportes",      lambda: reps.build(self.content, self.user)),
            ("Asistente AI",  lambda: advisor.build(self.content, self.user)),
            ("Perfil",        lambda: perfil.build(self.content, self.user)),
        ]

        self.btn_refs = {}      # Guardará referencias a los botones
        self.selected = None    # Botón actualmente seleccionado

        def navegar(name, fn):
            """
            Resalta el botón clicado y ejecuta su función:
            - Despinta el anterior (si existe).
            - Pinta el actual en verde.
            - Llama a la función fn() para renderizar contenido.
            """
            if self.selected:
                self.selected.configure(bg=COLOR_PRINCIPAL_AZUL)
            btn = self.btn_refs[name]
            btn.configure(bg=COLOR_VERDE_CRECIMIENTO)
            self.selected = btn
            fn()

        # Creamos botones dinámicamente
        for txt, fn in items:
            b = tk.Button(nav,
                          text=txt,
                          font=FONT_MENU,
                          fg=COLOR_BLANCO,
                          bg=COLOR_PRINCIPAL_AZUL,
                          relief="flat",
                          anchor="w",
                          padx=12,
                          pady=10,
                          command=lambda t=txt, f=fn: navegar(t, f)
                          )
            b.pack(fill="x", pady=2)
            self.btn_refs[txt] = b

        # -------------------------
        # 3) Botón Cerrar Sesión
        # -------------------------
        tk.Button(nav,
                  text="Cerrar Sesión",
                  font=FONT_MENU,
                  bg=COLOR_PELIGRO,
                  fg=COLOR_BLANCO,
                  relief="flat",
                  activebackground=COLOR_PELIGRO,
                  command=self._logout  # Lógica de logout
                  ).pack(side="bottom", fill="x", pady=20)

        # -------------------------
        # 4) Contenedor principal
        # -------------------------
        self.content = tk.Frame(self.win, bg=COLOR_FONDO_GRIS)
        self.content.pack(side="right", fill="both", expand=True)

        # Carga inicial: sección Home
        self._home()

    # =======================================================================================
    #  Secciones dinámicas: Home, o "sección principal"
    # =======================================================================================

    def _home(self):
        """
        Renderiza la vista de inicio:
        - Saludo personalizado usando nombre de perfil o email.
        - Selector de fechas y toggles de tipos de gráfico.
        - Tarjetas con saldo, ingresos y gastos.
        - Gráficas interactivas (barras, pastel y línea) según toggles.
        """
        # 1) Limpiamos cualquier widget anterior
        clear_frame(self.content)

        # 2) Cabecera con saludo
        uid = self.user["localId"]
        perfil_data, _ = fb.get_profile(uid)
        nombre = perfil_data.get("nombre") or self.user["email"]
        header = tk.Frame(self.content, bg=COLOR_FONDO_GRIS)
        header.pack(fill="x", pady=(8, 4), padx=6)
        tk.Label(header,
                 text=f"¡Bienvenido/a {nombre}!",
                 font=FONT_TITLE,
                 bg=COLOR_FONDO_GRIS,
                 fg=COLOR_PRINCIPAL_AZUL
                 ).pack(side="left")

        # Posible foto de perfil clicable para ir a la sección Perfil
        foto_path = perfil_data.get("foto")
        if foto_path and os.path.exists(foto_path):
            try:
                img = Image.open(foto_path)\
                           .resize((60, 60), Image.Resampling.LANCZOS)
                # Creamos máscara circular
                mask = Image.new("L", (60, 60), 0)
                ImageDraw.Draw(mask).ellipse((0, 0, 60, 60), fill=255)
                img.putalpha(mask)
                ph = ImageTk.PhotoImage(img)
                pic = tk.Label(header, image=ph,
                               bg=COLOR_FONDO_GRIS,
                               cursor="hand2")
                pic.image = ph
                pic.pack(side="right")
                # Al click invocamos botón de 'Perfil'
                pic.bind("<Button-1>",
                         lambda e: self.btn_refs["Perfil"].invoke())
            except Exception:
                pass

        # 3) Rango total de datos (para limitar DateEntry)
        raw, _ = fb.get_transactions(uid)
        fechas = [datetime.fromtimestamp(v["fecha"]).date()
                  for v in (raw or {}).values() if "fecha" in v]
        if fechas:
            min_date, max_date = min(fechas), max(fechas)
        else:
            max_date = date.today()
            min_date = max_date - timedelta(days=30)
            min_date = max_date

        # 4) Barra de filtros: periodo rápido + selectores
        toolbar = tk.Frame(self.content, bg=COLOR_FONDO_GRIS)
        toolbar.pack(fill="x", padx=6, pady=(0, 4))

        tk.Label(toolbar,
                 text="Periodo:",
                 bg=COLOR_FONDO_GRIS,
                 fg=COLOR_TEXTO_GRIS,
                 font=FONT_NORMAL
                 ).pack(side="left")

        opciones = ["Personalizado", "Hoy", "Semanal", "Quincenal",
                    "Mensual", "Trimestral", "Semestral", "Anual"]
        period_var = tk.StringVar(value="Mensual")
        cb_period = ttk.Combobox(toolbar,
                                 values=opciones,
                                 width=12,
                                 state="readonly",
                                 textvariable=period_var
                                 )
        cb_period.pack(side="left", padx=4)

        # DateEntry “Desde”
        tk.Label(toolbar,
                 text="Desde:",
                 bg=COLOR_FONDO_GRIS,
                 fg=COLOR_TEXTO_GRIS,
                 font=FONT_NORMAL
                 ).pack(side="left")
        date_from = DateEntry(toolbar,
                              date_pattern="yyyy-mm-dd",
                              mindate=min_date,
                              maxdate=max_date
                              )
        date_from.pack(side="left", padx=4)
        date_from.set_date(min_date)

        # DateEntry “Hasta”
        tk.Label(toolbar,
                 text="Hasta:",
                 bg=COLOR_FONDO_GRIS,
                 fg=COLOR_TEXTO_GRIS,
                 font=FONT_NORMAL
                 ).pack(side="left")
        date_to = DateEntry(toolbar,
                            date_pattern="yyyy-mm-dd",
                            mindate=min_date,
                            maxdate=max_date
                            )
        date_to.pack(side="left", padx=4)
        date_to.set_date(max_date)

        btn_apply = ttk.Button(toolbar, text="Aplicar filtro")
        btn_apply.pack(side="left", padx=6)

        # Toggles para mostrar/ocultar tipos de gráfico
        show_bar  = tk.BooleanVar(value=True)
        show_pie  = tk.BooleanVar(value=True)
        show_line = tk.BooleanVar(value=True)
        ttk.Checkbutton(toolbar, text="Barras", variable=show_bar).pack(side="left", padx=2)
        ttk.Checkbutton(toolbar, text="Pastel", variable=show_pie).pack(side="left", padx=2)
        ttk.Checkbutton(toolbar, text="Saldo",  variable=show_line).pack(side="left", padx=2)

        # 5) Contenedor 'resumen' para tarjetas y gráficos
        resumen = tk.Frame(self.content, bg=COLOR_FONDO_GRIS)
        resumen.pack(fill="both", expand=True)

        # ---------------------------------------------
        # Función interna: renderizar tarjetas y gráficos
        # ---------------------------------------------
        def render():
            # Limpia contenido previo
            clear_frame(resumen)

            # Construye DataFrame con todas las transacciones
            df = pd.DataFrame(list((raw or {}).values()))
            if df.empty:
                # Si no hay datos, mostramos mensaje
                tk.Label(resumen,
                         text="Sin movimientos registrados.",
                         bg=COLOR_FONDO_GRIS,
                         fg=COLOR_TEXTO_GRIS,
                         font=FONT_NORMAL
                         ).pack(pady=30)
                return

            # Convertimos timestamp a datetime
            df["fecha"] = pd.to_datetime(df["fecha"], unit="s")

            # Filtramos por rango seleccionado
            d0 = date_from.get_date()
            d1 = date_to.get_date() + timedelta(days=1)
            df_r = df[(df["fecha"] >= pd.Timestamp(d0)) &
                      (df["fecha"] <  pd.Timestamp(d1))].copy()

            # Calculamos totales: ingresos, gastos, saldo
            df_r["signed"] = df_r.apply(
                lambda r: r["monto"] if r["tipo"]=="Ingreso" else -r["monto"], axis=1
            )
            saldo = df_r["signed"].sum()
            ing   = df_r[df_r["tipo"]=="Ingreso"]["monto"].sum()
            gas   = df_r[df_r["tipo"]=="Gasto"]["monto"].sum()

            # --- Tarjetas de resumen ---
            cards = tk.Frame(resumen, bg=COLOR_FONDO_GRIS)
            cards.pack(fill="x")
            cards.columnconfigure((0,1,2), weight=1, uniform="col")

            def card(col, title, val, color):
                f = tk.Frame(cards, bg=color, padx=14, pady=10,
                             highlightbackground="#d5d9dd",
                             highlightthickness=1)
                tk.Label(f, text=title,
                         font=("Lato",12,"bold"),
                         bg=color,
                         fg=COLOR_BLANCO
                         ).pack()
                tk.Label(f, text=f"${val:,.0f}".replace(",","."), 
                         font=("Lato",18,"bold"),
                         bg=color,
                         fg=COLOR_BLANCO
                         ).pack()
                f.grid(row=0, column=col, padx=6, sticky="ew")

            card(0, "Saldo",   saldo, COLOR_PRINCIPAL_AZUL)
            card(1, "Ingresos", ing,  COLOR_VERDE_CRECIMIENTO)
            card(2, "Gastos",  -gas,  COLOR_ROJO_GASTO)

            # --- Gráficos dinámicos ---
            row = tk.Frame(resumen, bg=COLOR_FONDO_GRIS)
            row.pack(fill="x", pady=8)
            row.columnconfigure((0,1), weight=1, uniform="row")

            # Barras Ingresos vs Gastos
            if show_bar.get():
                fig, ax = plt.subplots(figsize=(5,3))
                ax.bar(["Ingresos","Gastos"], [ing, gas])
                ax.set_ylabel("$ COP")
                ax.set_title("Ingresos vs Gastos", fontweight="bold")
                ax.grid(axis="y", linestyle="--", alpha=0.3)
                fig.tight_layout()
                canvas = FigureCanvasTkAgg(fig, master=row)
                canvas.draw()
                canvas.get_tk_widget().grid(row=0, column=0, padx=4, sticky="nsew")
                plt.close(fig)

            # Pastel: distribución de gastos por categoría
            if show_pie.get():
                gastos_cat = (df_r[df_r["tipo"]=="Gasto"]
                              .groupby("categoria")["monto"].sum())
                if not gastos_cat.empty:
                    fig2, ax2 = plt.subplots(figsize=(5,3))
                    ax2.pie(gastos_cat,
                            labels=gastos_cat.index,
                            autopct="%1.0f%%",
                            startangle=90)
                    ax2.set_title("Distribución de Gastos", fontweight="bold")
                    fig2.tight_layout()
                    canvas2 = FigureCanvasTkAgg(fig2, master=row)
                    canvas2.draw()
                    canvas2.get_tk_widget().grid(row=0, column=1, padx=4, sticky="nsew")
                    plt.close(fig2)

            # Línea: saldo acumulado en el periodo
            if show_line.get():
                fig3, ax3 = plt.subplots(figsize=(10,3))
                serie = (df_r.sort_values("fecha")
                         .set_index("fecha")["signed"]
                         .cumsum()
                         .resample("D").last().ffill())
                ax3.plot(serie.index, serie.values, linewidth=2)
                ax3.axhline(0, linestyle="--", linewidth=0.7)
                ax3.fill_between(serie.index, serie.values,
                                 where=serie.values>=0, alpha=0.15)
                ax3.fill_between(serie.index, serie.values,
                                 where=serie.values<0, alpha=0.15)
                ax3.set_ylabel("$ COP")
                ax3.set_title("Saldo Acumulado", fontweight="bold")
                ax3.grid(axis="y", linestyle="--", alpha=0.3)
                fig3.tight_layout()
                canvas3 = FigureCanvasTkAgg(fig3, master=resumen)
                canvas3.draw()
                canvas3.get_tk_widget().pack(pady=(6,10), fill="x")
                plt.close(fig3)

        # Asignamos la función al botón Aplicar filtro
        btn_apply.configure(command=render)
        # Render inicial
        render()

        # -------------------------
        # Gestión de periodos rápidos
        # -------------------------
        def on_period_change(*_):
            p = period_var.get()
            hoy = date.today()
            # Restauramos selectores y habilitamos DateEntry
            date_from.config(state="normal")
            date_to.config(state="normal")

            if p == "Hoy":
                d0 = d1 = hoy
            elif p == "Semanal":
                d0 = hoy - timedelta(days=7); d1 = hoy
            elif p == "Quincenal":
                d0 = hoy - timedelta(days=15); d1 = hoy
            elif p == "Mensual":
                d0 = hoy.replace(day=1); d1 = hoy
            elif p == "Trimestral":
                d0 = (hoy - pd.DateOffset(months=3)).date(); d1 = hoy
            elif p == "Semestral":
                d0 = (hoy - pd.DateOffset(months=6)).date(); d1 = hoy
            elif p == "Anual":
                d0 = hoy.replace(month=1, day=1); d1 = hoy
            else:
                return  # personalizado

            # Clampeamos al mínimo y máximo disponibles
            if d0 < min_date: d0 = min_date
            if d1 > max_date: d1 = max_date

            date_from.set_date(d0)
            date_to.set_date(d1)
            # Deshabilitamos campos si no es personalizado
            if p != "Personalizado":
                date_from.config(state="disabled")
                date_to.config(state="disabled")

            render()

        period_var.trace_add("write", on_period_change)

    # =======================================================================================
    #  Logout: cierra esta ventana y regresa al login
    # =======================================================================================

    def _logout(self):
        import ui_login as login_module
        self.win.destroy()           # Cierra el Dashboard
        login_module.start(self.root)  # Vuelve a la ventana de login
