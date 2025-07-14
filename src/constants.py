# constants.py – KlarityFinanzasApp
# ======================================================================================
# Este archivo centraliza la identidad visual (colores, tipografías) y textos reutilizables
# en toda la aplicación KlarityFinanzasApp.
# 
# Cambiar cualquier valor aquí se reflejará inmediatamente en toda la aplicación.
# ======================================================================================


# ======================================================================================
# 1. PALETA DE COLORES
# ======================================================================================

# Azul oscuro principal, usado para fondos, elementos destacados y barras laterales.
COLOR_PRINCIPAL_AZUL = "#2C3E50"

# Verde usado para representar acciones positivas como ingresos o botones de confirmación.
COLOR_VERDE_CRECIMIENTO = "#2ECC71"

# Rojo para indicar gastos, errores o acciones negativas (por ejemplo, eliminar o cerrar sesión).
COLOR_ROJO_GASTO = "#E74C3C"

# Gris claro para fondos principales, otorgando un aspecto limpio y claro a las interfaces.
COLOR_FONDO_GRIS = "#ECF0F1"

# Gris oscuro para textos generales y etiquetas que requieren contraste contra el fondo gris.
COLOR_TEXTO_GRIS = "#34495E"

# Blanco puro usado principalmente para textos sobre fondos oscuros y botones.
COLOR_BLANCO = "#FFFFFF"

# Azul brillante utilizado para enlaces o textos clicables.
COLOR_LINK_AZUL = "#3498DB"

# Rojo intenso para resaltar elementos peligrosos o importantes (acciones irreversibles).
COLOR_PELIGRO = "#E74C3C"  # Añadido especialmente para alertas de peligro.


# ======================================================================================
# 2. TIPOGRAFÍAS
# ======================================================================================
# Nota importante:
# Estas fuentes asumen que la tipografía "Lato" está instalada en el sistema operativo.
# Si no está disponible, tkinter usará una fuente alternativa por defecto.

# Fuente negrita estándar para títulos secundarios o resaltados.
FONT_BOLD = ("Lato", 16, "bold")

# Fuente de gran tamaño y negrita usada principalmente para títulos principales.
FONT_TITLE = ("Lato", 24, "bold")

# Fuente normal para textos generales en la aplicación.
FONT_NORMAL = ("Lato", 12)

# Fuente cursiva para mostrar slogans o frases destacadas.
FONT_SLOGAN = ("Lato", 14, "italic")

# Fuente específica para elementos de menú lateral o superior.
FONT_MENU = ("Lato", 14)


# ======================================================================================
# 3. CATEGORÍAS POR DEFECTO
# ======================================================================================
# Estas categorías se crean automáticamente cuando un usuario se registra por primera vez.
DEFAULT_CATEGORIES = [
    {"nombre": "Alimentos",   "tipo": "Gasto"},     # Gastos generales en comida.
    {"nombre": "Transporte",  "tipo": "Gasto"},     # Gastos en transporte público o privado.
    {"nombre": "Salario",     "tipo": "Ingreso"},   # Ingreso fijo mensual o regular.
    {"nombre": "Ocio",        "tipo": "Gasto"},     # Gastos en entretenimiento, hobbies, etc.
    {"nombre": "Servicios",   "tipo": "Gasto"},     # Servicios básicos (agua, electricidad, internet).
    {"nombre": "Regalías",    "tipo": "Ingreso"}    # Ingresos por derechos o regalías.
]


# ======================================================================================
# 4. OTROS TEXTOS REUTILIZABLES
# ======================================================================================

# Slogan oficial de la aplicación, usado principalmente en splash screens y marketing.
APP_SLOGAN = "Finanzas claras, Futuro Seguro."

# Nombre oficial de la aplicación (usado en ventanas, títulos y otros elementos).
APP_NAME = "Klarity"
