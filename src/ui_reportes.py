# ===========================================================================================
# ui_reportes.py
# -------------------------------------------------------------------------------------------
# Módulo para generar reportes financieros:
# - Filtrado por rangos y presets de fecha.
# - Cálculo de resúmenes de ingresos, gastos y saldo.
# - Visualización de múltiples gráficos (pie, barras, líneas).
# - Interpretación automática con Gemini (IA).
# - Exportación a PDF (opcional, usando ReportLab).
# ===========================================================================================

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from tkcalendar import DateEntry
from datetime import datetime, date, timedelta
import json

import pandas as pd                           # Para manipulación de datos
import matplotlib.pyplot as plt               # Para generar gráficos
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from constants import *                       # Colores, fuentes, constantes
from utils import clear_frame                 # Limpia el contenedor antes de renderizar
import firebase_service as fb                 # Lógica CRUD de transacciones

# ─── Configuración de Gemini (Google Generative AI) ──────────────────────────────────
# Añadimos carpeta config al path para importar gemini_config.py
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
config_dir = os.path.join(project_root, 'config')
if config_dir not in sys.path:
    sys.path.append(config_dir)
from gemini_config import GEMINI_API_KEY       # Clave API para Gemini

# ─── Inicialización de Gemini ─────────────────────────────────────────────────────────
model = None
try:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    # Seleccionamos el modelo deseado
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
except Exception as e:
    # Si falla, seguimos sin IA pero informamos en consola
    print(f"[ui_reportes] No se pudo inicializar Gemini: {e}")

# Para exportar a PDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO


def build(frame: tk.Frame, user: dict):
    """
    Construye la UI de Reportes dentro de 'frame':
    - Carga datos.
    - Crea controles de filtro.
    - Muestra tarjetas de resumen.
    - Dibuja gráficos dinámicos.
    - Permite interpretación con IA.
    """

    # 1) Limpiar contenedor
    clear_frame(frame)
    uid = user['localId']

    # 2) Cargar todas las transacciones
    raw, _ = fb.get_transactions(uid)

    # ──────────────────────────────────────────────────────────────────────────
    # 3) Cabecera: Título, presets y selectores de fecha
    # ──────────────────────────────────────────────────────────────────────────

    header = tk.Frame(frame, bg=COLOR_FONDO_GRIS)
    header.pack(fill='x', padx=10, pady=10)

    tk.Label(
        header,
        text="Reportes",
        font=FONT_TITLE,
        bg=COLOR_FONDO_GRIS,
        fg=COLOR_PRINCIPAL_AZUL
    ).pack(side='left')

    # Determinar rango real de fechas en datos
    if raw:
        fechas = [datetime.fromtimestamp(v['fecha']).date()
                  for v in raw.values() if 'fecha' in v]
        min_date, max_date = min(fechas), max(fechas)
    else:
        # Por defecto último mes
        max_date = date.today()
        min_date = max_date - timedelta(days=30)

    # Presets de periodo
    period_var = tk.StringVar(value='Mensual')
    presets = ['Personalizado', 'Hoy', 'Semanal', 'Mensual', 'Anual']
    cb_period = ttk.Combobox(
        header,
        values=presets,
        textvariable=period_var,
        state='readonly',
        width=12
    )
    cb_period.pack(side='left', padx=5)

    # DateEntry “Desde”
    date_from = DateEntry(
        header,
        date_pattern='yyyy-mm-dd',
        mindate=min_date,
        maxdate=max_date
    )
    date_from.set_date(min_date)
    date_from.pack(side='left', padx=5)

    # DateEntry “Hasta”
    date_to = DateEntry(
        header,
        date_pattern='yyyy-mm-dd',
        mindate=min_date,
        maxdate=max_date
    )
    date_to.set_date(max_date)
    date_to.pack(side='left', padx=5)

    # Botón Aplicar
    btn_apply = tk.Button(
        header,
        text="Aplicar",
        bg=COLOR_VERDE_CRECIMIENTO,
        fg=COLOR_BLANCO,
        relief='flat',
        command=lambda: refresh_dashboard()
    )
    btn_apply.pack(side='left', padx=5)

    # Cuando cambie el preset, ajustamos fechas automáticamente
    def on_preset(*_):
        hoy = date.today()
        p = period_var.get()

        if p == 'Hoy':
            date_from.set_date(hoy); date_to.set_date(hoy)
        elif p == 'Semanal':
            date_from.set_date(hoy - timedelta(days=7)); date_to.set_date(hoy)
        elif p == 'Mensual':
            date_from.set_date(hoy.replace(day=1)); date_to.set_date(hoy)
        elif p == 'Anual':
            date_from.set_date(hoy.replace(month=1, day=1)); date_to.set_date(hoy)
        else:
            date_from.set_date(min_date); date_to.set_date(max_date)

        refresh_dashboard()

    period_var.trace_add('write', on_preset)


    # ──────────────────────────────────────────────────────────────────────────
    # 4) Resumen: tarjetas de Ingresos, Gastos y Saldo + botón Interpretar IA
    # ──────────────────────────────────────────────────────────────────────────

    summary = tk.Frame(frame, bg=COLOR_FONDO_GRIS)
    summary.pack(fill='x', padx=10, pady=(0,10))

    def make_card(parent, title, color):
        """
        Crea una “tarjeta” con fondo de color:
        - title: texto superior.
        - color: fondo (verde, rojo, azul).
        Devuelve el frame y la Label de valor.
        """
        f = tk.Frame(parent, bg=color, padx=12, pady=8)
        tk.Label(f, text=title, font=FONT_NORMAL, bg=color, fg=COLOR_BLANCO).pack()
        lbl = tk.Label(f, text="$0", font=FONT_TITLE, bg=color, fg=COLOR_BLANCO)
        lbl.pack()
        return f, lbl

    f_ing, lbl_ing = make_card(summary, "Ingresos", COLOR_VERDE_CRECIMIENTO)
    f_gas, lbl_gas = make_card(summary, "Gastos", COLOR_ROJO_GASTO)
    f_sal, lbl_sal = make_card(summary, "Saldo", COLOR_PRINCIPAL_AZUL)

    # Grid para las tarjetas, tres columnas igualitarias
    for i, f in enumerate((f_ing, f_gas, f_sal)):
        f.grid(row=0, column=i, padx=6, sticky='ew')
        summary.columnconfigure(i, weight=1)

    # Botón “Interpretar” que usa IA para comentar gráficos
    btn_interp = tk.Button(
        summary,
        text="Interpretar",
        bg=COLOR_PRINCIPAL_AZUL,
        fg=COLOR_BLANCO,
        relief='flat',
        command=lambda: interpretar()
    )
    btn_interp.grid(row=0, column=3, padx=6)


    # ──────────────────────────────────────────────────────────────────────────
    # 5) Panel principal: opciones de series y contenedor de gráficos + interpretación
    # ──────────────────────────────────────────────────────────────────────────

    main = tk.Frame(frame, bg=COLOR_FONDO_GRIS)
    main.pack(fill='both', expand=True, padx=10, pady=5)

    # Panel izquierdo: checkboxes para cada serie a mostrar
    left = tk.Frame(main, bg=COLOR_FONDO_GRIS)
    left.pack(side='left', fill='y', padx=(0,10))
    tk.Label(left, text="Series", bg=COLOR_FONDO_GRIS).pack(pady=(0,5))

    sel_vars = {}
    opts = [
        ("Gastos x Cat.",    'g1'),
        ("Ingresos vs Gastos", 'g2'),
        ("Saldo Acumulado",   'g3'),
        ("Top 5 Categorías",  'g4'),
    ]
    # Creamos un BooleanVar para cada opción
    for txt, key in opts:
        var = tk.BooleanVar(value=True)
        sel_vars[key] = var
        ttk.Checkbutton(left, text=txt, variable=var).pack(anchor='w')

    # Contenedor central para gráficos (canvas Matplotlib)
    center = tk.Frame(main, bg=COLOR_FONDO_GRIS)
    center.pack(side='left', fill='both', expand=True)
    fig = plt.Figure(figsize=(8,5))
    canvas = FigureCanvasTkAgg(fig, master=center)
    canvas.get_tk_widget().pack(fill='both', expand=True)

    # Panel derecho: cuadro de texto para interpretación IA
    right = tk.Frame(main, bg=COLOR_FONDO_GRIS)
    right.pack(side='left', fill='y', padx=(10,0))
    tk.Label(right, text="Interpretación", bg=COLOR_FONDO_GRIS).pack()
    txt_interp = ScrolledText(right, width=30, state='disabled')
    txt_interp.pack(fill='both', expand=True)


    # ──────────────────────────────────────────────────────────────────────────
    # 6) Función para filtrar DataFrame según fechas seleccionadas
    # ──────────────────────────────────────────────────────────────────────────

    def get_filtered_df():
        # Construimos datetime de inicio y fin
        d0 = datetime.combine(date_from.get_date(), datetime.min.time())
        d1 = datetime.combine(date_to.get_date(), datetime.max.time())
        df = pd.DataFrame(list((raw or {}).values()))
        if df.empty:
            return df
        df['fecha'] = pd.to_datetime(df['fecha'], unit='s')
        # Retornamos solo filas dentro del rango
        return df[(df['fecha'] >= d0) & (df['fecha'] <= d1)]


    # ──────────────────────────────────────────────────────────────────────────
    # 7) Refresh: recalcula resúmenes, limpia y redibuja todos los gráficos
    # ──────────────────────────────────────────────────────────────────────────

    def refresh_dashboard():
        df = get_filtered_df()
        # Cálculo de totales
        ingresos = df[df['tipo']=='Ingreso']['monto'].sum() if not df.empty else 0
        gastos   = df[df['tipo']=='Gasto']['monto'].sum()   if not df.empty else 0
        saldo    = ingresos - gastos

        # Actualizamos valores en las tarjetas
        lbl_ing.config(text=f"${ingresos:,.0f}".replace(',', '.'))
        lbl_gas.config(text=f"${gastos:,.0f}".replace(',', '.'))
        lbl_sal.config(text=f"${saldo:,.0f}".replace(',', '.'))

        # Limpiamos figura y ajustamos espacio
        fig.clf()
        fig.subplots_adjust(hspace=0.4, wspace=0.4)

        # Armamos lista de series a dibujar
        series = []
        df_sorted = df.sort_values('fecha') if not df.empty else df

        # 7.1) Pie chart: Gastos por Categoría
        if sel_vars['g1'].get() and not df.empty:
            g1 = df[df['tipo']=='Gasto'].groupby('categoria')['monto'].sum()
            series.append(('Gastos x Categoría', g1, 'pie'))

        # 7.2) Bar chart: Ingresos vs Gastos
        if sel_vars['g2'].get() and not df.empty:
            series.append(('Ingresos vs Gastos',
                           pd.Series({'Ingresos': ingresos, 'Gastos': gastos}),
                           'bar'))

        # 7.3) Line chart: Saldo Acumulado diario
        if sel_vars['g3'].get() and not df_sorted.empty:
            df2 = df_sorted.copy()
            df2['signed'] = df2.apply(
                lambda r: r['monto'] if r['tipo']=='Ingreso' else -r['monto'],
                axis=1
            )
            # Cálculo de cumsum diario, rellenando días sin transacciones
            serie_acum = df2.set_index('fecha')['signed'] \
                            .cumsum().resample('D').last().ffill()
            series.append(('Saldo Acumulado', serie_acum, 'line'))

        # 7.4) Barh chart: Top 5 categorías de Gasto
        if sel_vars['g4'].get() and not df.empty:
            g4 = df[df['tipo']=='Gasto'].groupby('categoria')['monto'].sum()
            g4 = g4.sort_values(ascending=False).head(5)
            series.append(('Top 5 Categorías', g4, 'barh'))

        # Insertamos cada subplot
        for idx, (title, data, kind) in enumerate(series):
            ax = fig.add_subplot(2, 2, idx+1)
            if kind == 'pie':
                data.plot.pie(ax=ax, autopct='%1.0f%%', startangle=90)
            elif kind == 'bar':
                data.plot.bar(ax=ax)
            elif kind == 'line':
                data.plot(ax=ax)
            elif kind == 'barh':
                data.plot.barh(ax=ax)
                ax.invert_yaxis()

            ax.set_title(title)
            ax.grid(axis='y', linestyle='--', alpha=0.3)

        # Redibujamos canvas
        canvas.draw()


    # Inicializamos dashboard al cargar
    refresh_dashboard()


    # ──────────────────────────────────────────────────────────────────────────
    # 8) Interpretación IA: genera texto explicativo para cada gráfico
    # ──────────────────────────────────────────────────────────────────────────

    def interpretar():
        df = get_filtered_df()
        ingresos = df[df['tipo']=='Ingreso']['monto'].sum() if not df.empty else 0
        gastos   = df[df['tipo']=='Gasto']['monto'].sum()   if not df.empty else 0

        txt_interp.configure(state='normal')
        txt_interp.delete('1.0', 'end')

        # Recorremos cada serie activa para pedir interpretación
        for key, var in sel_vars.items():
            if not var.get():
                continue

            # Preparamos datos según tipo de gráfico
            if key == 'g1':
                s = df[df['tipo']=='Gasto'].groupby('categoria')['monto'].sum().to_dict()
                title = 'Gastos x Categoría'
            elif key == 'g2':
                s = {'Ingresos': ingresos, 'Gastos': gastos}
                title = 'Ingresos vs Gastos'
            elif key == 'g3':
                df2 = df.copy()
                df2['signed'] = df2.apply(
                    lambda r: r['monto'] if r['tipo']=='Ingreso' else -r['monto'],
                    axis=1
                )
                s = df2.set_index('fecha')['signed'].cumsum() \
                       .resample('D').last().ffill().dropna().to_dict()
                title = 'Saldo Acumulado'
            else:
                tmp = df[df['tipo']=='Gasto'].groupby('categoria')['monto'].sum()
                s = tmp.sort_values(ascending=False).head(5).to_dict()
                title = 'Top 5 Categorías'

            # Montamos prompt para IA
            prompt = f"Interpreta el gráfico '{title}'. Datos: {json.dumps(s, indent=2)}"

            if model:
                try:
                    text = model.generate_content(prompt).text
                except Exception as e:
                    text = f"[Error de Gemini: {e}]"
            else:
                text = "[Gemini no disponible]"

            # Insertamos sección de interpretación
            txt_interp.insert('end', f"--- {title} ---\n{text}\n\n")

        txt_interp.configure(state='disabled')
