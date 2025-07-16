## Documentación de KlarityFinanzasApp

KlarityFinanzasApp es una aplicación de escritorio en Python que ayuda a gestionar finanzas personales. Aunque este es un proyecto en el que estoy aprendiendo, aquí explico de manera sencilla su funcionamiento.

---

### Requisitos y configuración

* Python 3.13.

  ```bash
  pip install -r requirements.txt
  ```
* Colocar `serviceAccountKey.json` en `config/` y ajustar `SERVICE_ACCOUNT_KEY_PATH` en `firebase_config.py`.
* colocarla la APYKEY de gemini en gemini_config.py` en `config/` con:

  ```python
  GEMINI_API_KEY = "TU_LLAVE_AQUI"
  ```

---


### 2. Requisitos y dependencias

* **Python 3.13**

* **Librerías de UI**:

  * `tkinter`: Framework nativo de Python para interfaces gráficas.
  * `tkcalendar`: Selector de fechas.
  * `Pillow`: Manipulación de imágenes (carga, redimensionado, máscaras).

* **Firebase**:

  * `pyrebase`: Cliente Firebase para autenticación, base de datos en tiempo real.
  * `firebase-admin`: Admin SDK para operaciones privilegiadas (cambio de contraseña, CRUD administrativo).

* **IA Generativa**:

  * `google.generativeai` (Gemini): Genera resúmenes, consejos y planes basados en transacciones.
  * `gemini_config.py`: Archivo con clave `GEMINI_API_KEY`.

* **Análisis y gráficos**:

  * `pandas`: Manipulación y filtrado de datos transaccionales.
  * `matplotlib`: Generación de gráficos (barras, pastel, líneas).

* **Utilidades**:

  * `tkinter.messagebox`: Diálogos de error, confirmación e información.
  * `os`, `sys`, `json`, `time`, `datetime`: Módulos estándar para manejo de archivos, rutas y tiempos.

---

### 3. Estructura de archivos

```
/KlarityFinanzasApp/
├── main.py                # Punto de entrada: inicia splash y login
├── ui_splash.py           # Pantalla de carga
├── ui_login.py            # Login y registro de usuarios
├── ui_dashboard.py        # Ventana principal y navegación
├── ui_transacciones.py    # Gestión de movimientos financieros
├── ui_categorias.py       # CRUD de categorías
├── ui_reportes.py         # Generación de reportes y exportación PDF
├── ui_ai_advisor.py       # Asesor financiero con Gemini
├── ui_perfil.py           # Visualización y edición de perfil
├── firebase_service.py    # Inicialización Firebase y funciones CRUD
├── utils.py               # Funciones auxiliares (limpiar frames, centrar ventanas, formateo)
├── constants.py           # Colores, tipografías, textos reutilizables
├── config/                # Claves y configuración
│   ├── firebase_config.py # FIREBASE_CONFIG, SERVICE_ACCOUNT_KEY_PATH
│   └── gemini_config.py   # GEMINI_API_KEY
└── assets/                # Imágenes (logo, íconos)
```

---

### 4. Flujo de ejecución


1. El usuario inicia sesión; la aplicación valida credenciales con **Firebase**.
2. Las transacciones se obtienen como un diccionario con `firebase_service.get_transactions(uid)`.
3. Con **Pandas** se convierte a `DataFrame`, se filtra por fechas y se calculan:

   * Ingresos: suma de montos con tipo "Ingreso".
   * Gastos: suma de montos con tipo "Gasto".
   * Saldo: diferencia entre ambos.
 Para dibujar gráficos se usa **Matplotlib** y se inserta en la interfaz con `FigureCanvasTkAgg`:

   * Gráfico de barras para ingresos vs. gastos.
   * Gráfico de pastel para distribución de gastos.
   * Gráfico de línea para saldo acumulado.

1. **main.py** inicia la app:
2. **Login / Registro** (`ui_login.py`):

   * Ventana **LoginWindow**: pide email y contraseña.
   * Usa `firebase_service.login_user()` y maneja errores.
   * Redirige a `DashboardWindow`.
   * Enlace para **RegisterWindow**: registra usuario y perfil.

3. **Dashboard** (`ui_dashboard.py`):

   * Construye barra lateral con botones de navegación.
   * Secciones: Transacciones, Categorías, Reportes, Asistente AI, Perfil.
   * Pestaña **Home**: muestra tarjetas de saldo, ingresos y gastos; gráficos dinámicos.
   * Usa `pandas` para procesar datos y `matplotlib` para graficar.

4. **Transacciones** (`ui_transacciones.py`):

   * Tabla con historial, ordenable y con filtros de fecha.
   * CRUD via `firebase_service`.

5. **Categorías** (`ui_categorias.py`):

   * Tabla con orden y búsquedas
   * CRUD con validaciones de nombre.

6. **Reportes** (`ui_reportes.py`):

   * Filtros de fecha y presets (Hoy, Semanal, Mensual, Anual).
   * Tarjetas resumen de ingresos, gastos y saldo.
   * Panel de gráficos múltiples:

     * Gastos por categoría.
     * Ingresos vs Gastos.
     * Saldo acumulado.
     * Top 5 categorías.
   * Botón **Interpretar** usa Gemini para describir gráficos.

7. **Asistente AI** (`ui_ai_advisor.py`):

   * Similar a Reportes pero con botones rápidos:

     * Resumen.
     * Consejos.
     * Plan de mejora.
   * Consulta libre: texto y transacciones.
   * Guarda historial en Firebase (`ai_sugerencias`).

8. **Perfil** (`ui_perfil.py`):

   * Muestra datos de usuario (nombre, foto).
   * Permite cambiar foto: uso de `filedialog` y `Pillow` para máscara circular.
   * Cambiar nombre y actualizar en Firebase.
   * Sección seguridad: reautenticar y cambiar contraseña con Admin SDK.

---

### 5. Integración de librerías clave

* **Pyrebase** (`pyrebase.initialize_app`) y **Firebase Admin**:

  * Autenticación (`auth.create_user_with_email_and_password`, `auth.sign_in_with_email_and_password`).
  * Reglas CRUD: `db.child("..."`) para usuarios, categorías, transacciones y sugerencias.
  * Cambio de contraseña: `admin_auth.update_user(uid, password=...)`.

* **Tkinter**:

  * Ventanas: `Tk()`, `Toplevel`, `Frames`, `Buttons`, `Labels`, `Entry`.
  * Layout: `.pack()`, `.grid()`, `.place()`.
  * Diálogos: `messagebox.showinfo`, `.showerror`, `.askyesno`.

* **Tkcalendar**:

  * `DateEntry` para selección de fechas con `mindate` y `maxdate`.

* **Pillow**:

  * Carga y redimensionado de imágenes (logo, avatar).
  * Creación de máscaras circulares en perfil y dashboard.

* **Pandas**:

  * Conversión de datos crudos (`timestamp`) a `DataFrame`.
  * Filtrado por rango de fechas.
  * Cálculo de ingresos, gastos, saldo y agrupaciones.

* **Matplotlib**:

  * Graficar barras, pastel y líneas.
  * Integración con Tkinter: `FigureCanvasTkAgg`.

* **Google Generative AI (Gemini)**:

  * Configuración: `genai.configure(api_key=GEMINI_API_KEY)`.
  * Modelo: `GenerativeModel("gemini-1.5-flash-latest")`.
  * Métodos: `model.generate_content(prompt).text`.

---

### 6. Lógica interna de la aplicación

Esta sección describe cómo fluye la información desde el almacenamiento en Firebase hasta la interfaz de usuario, y cómo se generan e interpretan los gráficos en toda la aplicación.


#### 6.1. Obtención y preprocesamiento de datos

Cada módulo principal de datos (Dashboard, Reportes, Asistente AI) inicia recuperando todas las transacciones con:

```python
raw, _ = firebase_service.get_transactions(uid)
# raw: dict { id: {'fecha': timestamp, 'monto': float, 'tipo': str, 'categoria': str, ...}, ... }
```

luego se extraen las fechas disponibles y se calcula `min_date` y `max_date`:

```python
fechas = [ datetime.fromtimestamp(v['fecha']).date() for v in raw.values() if 'fecha' in v ]
min_date, max_date = min(fechas), max(fechas)
```

Para filtrar por rango seleccionado, la aplicación convierte `raw` en un `DataFrame`, transforma la columna de fecha a tipo datetime y aplica las condiciones de filtrado:

```python
df = pd.DataFrame(list(raw.values()))
df['fecha'] = pd.to_datetime(df['fecha'], unit='s')
df_r = df[(df['fecha'] >= d0) & (df['fecha'] <= d1)]
```

#### 6.2. Generación de métricas y gráficos

Tras aplicar el filtro, la aplicación calcula:

* **Ingresos**: suma de `monto` donde `tipo == 'Ingreso'`.
* **Gastos**: suma de `monto` donde `tipo == 'Gasto'`.
* **Saldo**: diferencia entre ingresos y gastos.

A continuación, crea tarjetas informativas usando `tk.Frame` y `tk.Label` para mostrar cada valor con formato monetario.

Para los gráficos, la aplicación emplea Matplotlib y los integra en Tkinter gracias a FigureCanvasTkAgg:

1. **Ingresos vs Gastos** (Gráfico de barras):

   ```python
   fig, ax = plt.subplots()
   ax.bar(['Ingresos','Gastos'], [ing, gas])
   ```
2. **Distribución de Gastos** (Gráfico de pastel):

   ```python
   gastos_cat = df_r[df_r['tipo']=='Gasto'].groupby('categoria')['monto'].sum()
   fig2, ax2 = plt.subplots()
   ax2.pie(gastos_cat, labels=gastos_cat.index, autopct='%1.0f%%')
   ```
3. **Saldo Acumulado** (Gráfico de línea):

   ```python
   df2 = df_r.copy()
   df2['signed'] = df2.apply(lambda r: r['monto'] if r['tipo']=='Ingreso' else -r['monto'], axis=1)
   serie = df2.set_index('fecha')['signed'].cumsum().resample('D').last().ffill()
   fig3, ax3 = plt.subplots()
   ax3.plot(serie.index, serie.values)
   ```

Cada figura se renderiza con `FigureCanvasTkAgg(fig, master=...)`, se dibuja con `draw()` y se inserta en el layout de Tkinter.

#### 6.3. Interpretación con Gemini

##### 6.3.1. Diccionario en Reportes

Para cada serie de datos presentada en **Reportes**, la aplicación extrae un objeto Pandas (`Series` o `DataFrame`) y lo convierte a un diccionario de Python:

```python
series = df_r[df_r['tipo']=='Gasto'].groupby('categoria')['monto'].sum()
datos = series.to_dict()
```

Se formatea este diccionario en JSON e incorpora el resultado en un prompt:

```python
prompt = f"Interpreta el gráfico '{title}'. Datos: {json.dumps(datos, indent=2)}"
```

Gemini procesa el JSON estructurado y devuelve un texto interpretativo que se muestra en el panel de interpretación.

##### 6.3.2. Diccionario en Asistente AI

En la sección de **Asistente AI**, la aplicación no agrupa datos, sino que envía el conjunto de transacciones sin procesar dentro del rango seleccionado:

```python
txs = [ v for v in raw.values() if d0 <= v['fecha'] < d1 ]
json_txs = json.dumps(txs, indent=2)
prompt = template.format(desde=..., hasta=..., json_txs=json_txs)
```

Cada plantilla (`Resumen`, `Consejos`, `Plan de mejora`) reemplaza `{json_txs}` y se envía a Gemini, que devuelve el análisis correspondiente, el cual se muestra al usuario y se almacena en Firebase.
