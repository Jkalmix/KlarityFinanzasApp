# ===========================================================================================
# ui_ai_advisor.py
# -------------------------------------------------------------------------------------------
# Módulo “Asistente AI” de KlarityFinanzasApp:
# - Permite generar resúmenes, consejos y planes de mejora basados en transacciones.
# - Soporta consultas libres.
# - Almacena un historial de sugerencias en Firebase.
# - Utiliza Google Generative AI (Gemini) para el procesamiento de lenguaje.
# ===========================================================================================

import os
import sys
import json
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from datetime import datetime, date
from tkcalendar import DateEntry

from constants import (
    COLOR_FONDO_GRIS,
    COLOR_PRINCIPAL_AZUL,
    COLOR_VERDE_CRECIMIENTO,
    COLOR_BLANCO,
    COLOR_ROJO_GASTO,
    FONT_TITLE,
    FONT_NORMAL
)
from utils import clear_frame
import firebase_service as fb

# ─── Configuración para cargar la clave de Gemini ────────────────────────────────────────
# Obtenemos la carpeta raíz y agregamos 'config' al path para importar gemini_config.py
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
config_dir = os.path.join(project_root, 'config')
if config_dir not in sys.path:
    sys.path.append(config_dir)
from gemini_config import GEMINI_API_KEY  # Clave API de Google Generative AI

# ─── Inicialización de Gemini ─────────────────────────────────────────────────────────
model = None
try:
    # Importamos y configuramos el cliente de Gemini
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    # Seleccionamos el modelo deseado
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
except Exception as e:
    # Si falla la importación o configuración, se desactiva la IA
    print(f"[ui_ai_advisor] No se pudo inicializar Gemini: {e}")


def build(frame: tk.Frame, user: dict):
    """
    Construye la interfaz del Asistente AI:
    - Selector de fechas para filtrar transacciones.
    - Botones para generar resumen, consejos o plan de mejora.
    - Campo de consulta libre.
    - Área de texto para mostrar el resultado y listado histórico.
    """
    # 1) Limpiar contenedor
    clear_frame(frame)
    uid = user['localId']  # UID de Firebase

    # 2) Cargar todas las transacciones del usuario
    raw, _ = fb.get_transactions(uid)

    # 3) Determinar rango de fechas disponibles
    #    Usamos las marcas de tiempo para obtener fechas mín. y máx.
    fechas = [
        datetime.fromtimestamp(v['fecha']).date()
        for v in (raw or {}).values() if 'fecha' in v
    ]
    if fechas:
        min_date, max_date = min(fechas), max(fechas)
    else:
        # Si no hay datos, por defecto hoy
        max_date = date.today()
        min_date = max_date

    # ────────────────────────────────────────────────────────────────────────────
    # 4) Controles de filtro: Fecha Desde, Fecha Hasta y botones rápidos
    # ────────────────────────────────────────────────────────────────────────────

    ctrl = tk.Frame(frame, bg=COLOR_FONDO_GRIS)
    ctrl.pack(fill="x", padx=10, pady=(5,2))

    # Label y DateEntry “Desde”
    tk.Label(
        ctrl,
        text="Desde:",
        font=FONT_NORMAL,
        bg=COLOR_FONDO_GRIS,
        fg=COLOR_PRINCIPAL_AZUL
    ).pack(side="left")
    date_from = DateEntry(
        ctrl, date_pattern="yyyy-mm-dd",
        mindate=min_date, maxdate=max_date
    )
    date_from.set_date(min_date)
    date_from.pack(side="left", padx=4)

    # Label y DateEntry “Hasta”
    tk.Label(
        ctrl,
        text="Hasta:",
        font=FONT_NORMAL,
        bg=COLOR_FONDO_GRIS,
        fg=COLOR_PRINCIPAL_AZUL
    ).pack(side="left")
    date_to = DateEntry(
        ctrl, date_pattern="yyyy-mm-dd",
        mindate=min_date, maxdate=max_date
    )
    date_to.set_date(max_date)
    date_to.pack(side="left", padx=4)

    # Función interna para generar prompts y mostrar resultados
    def _generate(template: str):
        # 4.1) Verificamos que el modelo esté disponible
        if model is None:
            messagebox.showerror("API", "Gemini no está configurado.", parent=frame)
            return

        # 4.2) Filtrar transacciones por rango de fecha
        d0 = datetime.combine(date_from.get_date(), datetime.min.time()).timestamp()
        d1 = datetime.combine(date_to.get_date(), datetime.min.time()).timestamp() + 86400
        txs = [v for v in (raw or {}).values() if d0 <= v['fecha'] < d1]
        if not txs:
            messagebox.showinfo("Sin datos", "No hay transacciones en ese rango.", parent=frame)
            return

        # 4.3) Construir prompt usando la plantilla con datos JSON
        prompt = template.format(
            desde=date_from.get_date().isoformat(),
            hasta=date_to.get_date().isoformat(),
            json_txs=json.dumps(txs, indent=2)
        )

        # 4.4) Mostrar mensaje de espera y generar en fondo
        out.delete("1.0", tk.END)
        out.insert(tk.END, "Generando, por favor espera...")
        frame.update_idletasks()

        try:
            resp = model.generate_content(prompt).text
        except Exception as e:
            messagebox.showerror("Error API", str(e), parent=frame)
            return

        # 4.5) Guardar en Firebase y mostrar resultado
        fb.save_ai_suggestion(uid, resp)
        out.delete("1.0", tk.END)
        out.insert(tk.END, resp)
        load_history()  # Refrescar historial tras guardar

    # Botones rápidos que usan distintas plantillas de prompt
    tk.Button(
        ctrl, text="Resumen",
        bg=COLOR_PRINCIPAL_AZUL, fg=COLOR_BLANCO,
        font=FONT_NORMAL,
        command=lambda: _generate(
            "Resume mis transacciones entre {desde} y {hasta}:\n{json_txs}"
        )
    ).pack(side="left", padx=4)

    tk.Button(
        ctrl, text="Consejos",
        bg=COLOR_VERDE_CRECIMIENTO, fg=COLOR_BLANCO,
        font=FONT_NORMAL,
        command=lambda: _generate(
            "Basado en mis transacciones entre {desde} y {hasta}, dame 3 consejos breves para mejorar mis finanzas:\n{json_txs}"
        )
    ).pack(side="left", padx=4)

    tk.Button(
        ctrl, text="Plan de mejora",
        bg="#E67E22", fg=COLOR_BLANCO,
        font=FONT_NORMAL,
        command=lambda: _generate(
            "Basado en mis transacciones entre {desde} y {hasta}, elabora un plan de mejora en 3 pasos:\n{json_txs}"
        )
    ).pack(side="left", padx=4)


    # ────────────────────────────────────────────────────────────────────────────
    # 5) Consulta libre: campo de texto y botón “Enviar”
    # ────────────────────────────────────────────────────────────────────────────

    qframe = tk.Frame(frame, bg=COLOR_FONDO_GRIS)
    qframe.pack(fill="x", padx=10, pady=(2,5))

    tk.Label(
        qframe,
        text="Consulta libre:",
        font=FONT_NORMAL,
        bg=COLOR_FONDO_GRIS,
        fg=COLOR_PRINCIPAL_AZUL
    ).pack(side="left")

    entry_q = tk.Entry(qframe, width=50)
    entry_q.pack(side="left", padx=4)

    def _free():
        """
        Maneja consultas arbitrarias:
        - Incluye todas las transacciones en el prompt.
        """
        if model is None:
            messagebox.showerror("API", "Gemini no está configurado.", parent=frame)
            return

        question = entry_q.get().strip()
        if not question:
            return

        # Construcción del prompt con pregunta y datos completos
        prompt = (
            f"{question}\n\nAquí están mis transacciones:\n"
            f"{json.dumps(list((raw or {}).values()), indent=2)}"
        )

        out.delete("1.0", tk.END)
        out.insert(tk.END, "Generando respuesta…")
        frame.update_idletasks()

        try:
            resp = model.generate_content(prompt).text
        except Exception as e:
            messagebox.showerror("Error API", str(e), parent=frame)
            return

        fb.save_ai_suggestion(uid, resp)
        out.delete("1.0", tk.END)
        out.insert(tk.END, resp)
        load_history()

    tk.Button(
        qframe, text="Enviar",
        bg=COLOR_PRINCIPAL_AZUL, fg=COLOR_BLANCO,
        font=FONT_NORMAL,
        command=_free
    ).pack(side="left", padx=4)


    # ────────────────────────────────────────────────────────────────────────────
    # 6) Área de texto para salida de IA
    # ────────────────────────────────────────────────────────────────────────────

    out = scrolledtext.ScrolledText(frame, wrap="word", height=12)
    out.pack(fill="both", expand=True, padx=10, pady=5)


    # ────────────────────────────────────────────────────────────────────────────
    # 7) Historial de sugerencias: Treeview con fecha y extracto
    # ────────────────────────────────────────────────────────────────────────────

    hframe = tk.Frame(frame, bg=COLOR_FONDO_GRIS)
    hframe.pack(fill="both", expand=False, padx=10, pady=(0,10))

    tk.Label(
        hframe,
        text="Historial de sugerencias:",
        font=FONT_TITLE,
        bg=COLOR_FONDO_GRIS,
        fg=COLOR_PRINCIPAL_AZUL
    ).pack(anchor="w")

    cols = ("Fecha", "Extracto")
    tree = ttk.Treeview(hframe, columns=cols, show="headings", height=5)
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor="w")
    tree.pack(side="left", fill="both", expand=True)

    sb = ttk.Scrollbar(hframe, command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")


    # ────────────────────────────────────────────────────────────────────────────
    # 8) Funciones de gestión de historial
    # ────────────────────────────────────────────────────────────────────────────

    def load_history():
        """
        Recupera sugerencias de Firebase y las muestra en el Treeview.
        Solo mostramos fecha y primer renglón como extracto.
        """
        tree.delete(*tree.get_children())
        suggestions, _ = fb.get_ai_suggestions(uid)

        # Orden descendente por timestamp
        for ts_str, rec in sorted(suggestions.items(), reverse=True):
            try:
                dt = datetime.fromtimestamp(int(ts_str)).strftime("%Y-%m-%d %H:%M")
            except:
                dt = ts_str
            excerpt = rec["texto"].split("\n",1)[0]
            tree.insert("", "end", iid=ts_str, values=(dt, excerpt))

    def on_select(event):
        """
        Cuando el usuario selecciona un elemento del historial,
        mostramos el texto completo en el área de salida.
        """
        sel = tree.selection()
        if not sel:
            return
        ts = sel[0]
        suggestions, _ = fb.get_ai_suggestions(uid)
        text = suggestions.get(ts, {}).get("texto", "")
        out.delete("1.0", tk.END)
        out.insert(tk.END, text)

    def delete_selected():
        """
        Elimina la sugerencia seleccionada de Firebase y actualiza la vista.
        """
        sel = tree.selection()
        if not sel:
            return
        ts = sel[0]
        if not messagebox.askyesno("Confirmar", "¿Eliminar esta sugerencia?", parent=frame):
            return
        fb.delete_ai_suggestion(uid, ts)
        load_history()
        out.delete("1.0", tk.END)

    tree.bind("<<TreeviewSelect>>", on_select)

    btn_del = tk.Button(
        hframe,
        text="Eliminar sugerencia",
        bg=COLOR_ROJO_GASTO,
        fg=COLOR_BLANCO,
        font=FONT_NORMAL,
        command=delete_selected
    )
    btn_del.pack(pady=4)


    # ────────────────────────────────────────────────────────────────────────────
    # 9) Carga inicial del historial para mostrar al entrar
    # ────────────────────────────────────────────────────────────────────────────

    load_history()