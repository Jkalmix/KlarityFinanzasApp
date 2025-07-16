# config/firebase_config.py

import os

# Obtén el directorio base del script actual (que es 'config' en este caso)
# Ya que este archivo está en 'config', BASE_DIR será la ruta a la carpeta 'config'.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construye la ruta al archivo JSON de la cuenta de servicio
# Desde 'config/', simplemente especificamos el nombre exacto de tu archivo JSON.
SERVICE_ACCOUNT_KEY_PATH = os.path.join(BASE_DIR, 'Nombre de tu archivo.json')


# -------------------------------------------------------------
# CONFIGURACIÓN PARA PYREBASE (AUTENTICACIÓN DE USUARIOS, REALTIME DB CLIENTE)
# Esta configuración debe coincidir exactamente con la de tu "Aplicación web" en Firebase Console.
# -------------------------------------------------------------
FIREBASE_CONFIG = {
    "apiKey": "tu llave",
    "authDomain": "klarityfinanzasapp.firebaseapp.com",
    "databaseURL": "https://klarityfinanzasapp-default-rtdb.firebaseio.com/",
    "projectId": "klarityfinanzasapp",
    "storageBucket": "klarityfinanzasapp.appspot.com", # Corregido: debería ser .appspot.com, no .firebasestorage.app
    "messagingSenderId": "324130409551",
    "appId": "Tu appID",
    "measurementId": "G-5RSTHZBMWH", # Opcional, Pyrebase4 no lo usa directamente
}
# -------------------------------------------------------------
# FIN DE LA CONFIGURACIÓN FIREBASE_CONFIG
# NO incluyas "serviceAccount" directamente aquí, ya que es para Pyrebase Admin SDK
# y no para la inicialización de la app cliente con apiKey.
# -------------------------------------------------------------


# Línea de prueba para verificar la ruta (puedes borrarla después de confirmar)
print(f"La ruta del archivo de clave de servicio configurada es: {SERVICE_ACCOUNT_KEY_PATH}")
if not os.path.exists(SERVICE_ACCOUNT_KEY_PATH):
    print(f"ADVERTENCIA: ¡El archivo de clave de servicio NO se encontró en: {SERVICE_ACCOUNT_KEY_PATH}!")
    print("Por favor, verifica que el archivo JSON esté en la carpeta 'config' y que el nombre en el código coincida exactamente.")
