# src/firebase_service.py

import pyrebase
import os
import sys # Importa el módulo sys para manipular la ruta de búsqueda de módulos

# --- Configuración de la ruta para importar firebase_config.py ---
# Pyrebase necesita acceder a las credenciales de Firebase.
# Como firebase_config.py está en la carpeta 'config/' y firebase_service.py está en 'src/',
# necesitamos añadir 'config/' al sys.path para que Python pueda encontrarlo.
current_dir = os.path.dirname(os.path.abspath(__file__)) # Obtiene la ruta del directorio actual (src/)
# '..' sube un nivel al directorio raíz del proyecto (KlarityFinanzasApp/).
# Luego, 'config' especifica la carpeta donde se encuentra firebase_config.py.
config_dir = os.path.join(current_dir, '..', 'config')

# Añade la carpeta 'config' al sys.path si aún no está.
# Esto permite importar módulos directamente desde 'config' como si fueran paquetes.
if config_dir not in sys.path:
    sys.path.append(config_dir)

# Ahora que 'config' está en el sys.path, podemos importar firebase_config.py.
# Importa las credenciales de configuración de Firebase y la ruta de la clave de servicio.
from firebase_config import FIREBASE_CONFIG


# --- Inicialización de Firebase Services ---
# Se inicializa Firebase una sola vez cuando el módulo `firebase_service.py` es cargado.
# Esto crea instancias de los servicios de autenticación (auth) y base de datos (db)
# que serán utilizados por las demás funciones.
try:
    # Inicializa la aplicación Firebase con la configuración proporcionada.
    firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
    
    # Obtiene una instancia del servicio de autenticación de Firebase.
    auth = firebase.auth()
    
    # Obtiene una instancia del servicio de Realtime Database de Firebase.
    db = firebase.database()
    
    print("Firebase services (Auth, DB) inicializados correctamente.")
except Exception as e:
    # Si ocurre un error durante la inicialización, lo imprime en la consola.
    print(f"ERROR: No se pudo inicializar Firebase en firebase_service.py: {e}")
    print("Asegúrate de que firebase_config.py es correcto y que las credenciales de tu proyecto Firebase son válidas.")
    # Considera si deseas que la aplicación se cierre o manejar este error de forma más robusta
    # si la conexión a Firebase es crítica para su funcionamiento.
    # Por ejemplo, podrías lanzar una excepción o salir de la aplicación:
    # raise Exception("Fallo crítico: No se pudo conectar a Firebase.")
    # sys.exit(1)


# --- Funciones de Autenticación de Usuarios ---

def register_user(email, password):
    """
    Registra un nuevo usuario en Firebase Authentication con email y contraseña.

    Args:
        email (str): El correo electrónico del nuevo usuario.
        password (str): La contraseña para el nuevo usuario.

    Returns:
        tuple: Una tupla conteniendo:
            - dict: Un diccionario con los datos del usuario registrado si la operación
                    fue exitosa (ej. {'email': '...', 'localId': 'UID', ...}).
            - None: Si no hubo errores.
        tuple: O bien:
            - None: Si la operación falló.
            - str: Un mensaje de error descriptivo.
    """
    try:
        # Intenta crear un nuevo usuario en Firebase Authentication.
        user = auth.create_user_with_email_and_password(email, password)
        print(f"Usuario registrado exitosamente: {user['email']}")
        return user, None # Devuelve los datos del usuario y None para el error
    except Exception as e:
        error_message = str(e) # Convierte el objeto de excepción a cadena para analizar el mensaje
        print(f"Error en register_user: {error_message}") # Imprime el error completo para depuración
        
        # Mapea los errores comunes de Firebase a mensajes más amigables para el usuario.
        if "EMAIL_EXISTS" in error_message:
            return None, "Este correo electrónico ya está registrado."
        elif "WEAK_PASSWORD" in error_message:
            return None, "La contraseña es demasiado débil (mínimo 6 caracteres)."
        elif "INVALID_EMAIL" in error_message:
            return None, "El formato del correo electrónico no es válido."
        else:
            # Para cualquier otro error inesperado, devuelve el mensaje de error original.
            return None, f"Error al registrar usuario: {error_message}"

def login_user(email, password):
    """
    Inicia sesión a un usuario existente en Firebase Authentication con email y contraseña.

    Args:
        email (str): El correo electrónico del usuario.
        password (str): La contraseña del usuario.

    Returns:
        tuple: Una tupla conteniendo:
            - dict: Un diccionario con los datos del usuario logueado si la operación
                    fue exitosa.
            - None: Si no hubo errores.
        tuple: O bien:
            - None: Si la operación falló.
            - str: Un mensaje de error descriptivo.
    """
    try:
        # Intenta iniciar sesión con el email y la contraseña proporcionados.
        user = auth.sign_in_with_email_and_password(email, password)
        print(f"Usuario logueado exitosamente: {user['email']}")
        return user, None # Devuelve los datos del usuario y None para el error
    except Exception as e:
        error_message = str(e) # Convierte el objeto de excepción a cadena
        print(f"Error en login_user: {error_message}") # Imprime el error completo para depuración

        # Mapea los errores comunes de Firebase a mensajes más amigables.
        if "EMAIL_NOT_FOUND" in error_message:
            return None, "Usuario no encontrado. Verifica el correo electrónico."
        elif "INVALID_PASSWORD" in error_message:
            return None, "Contraseña incorrecta."
        elif "USER_DISABLED" in error_message:
            return None, "Esta cuenta ha sido deshabilitada."
        else:
            # Para otros errores, devuelve el mensaje de error original.
            return None, f"Error al iniciar sesión: {error_message}"

# Puedes añadir más funciones relacionadas con la autenticación aquí, por ejemplo:
# def reset_password(email):
#     """Envía un correo de restablecimiento de contraseña al email dado."""
#     try:
#         auth.send_password_reset_email(email)
#         return True, "Se ha enviado un correo para restablecer tu contraseña."
#     except Exception as e:
#         return False, f"Error al enviar correo de restablecimiento: {e}"

# def send_email_verification(user_id_token):
#     """Envía un correo de verificación al usuario."""
#     try:
#         auth.send_email_verification(user_id_token)
#         return True, "Se ha enviado un correo de verificación."
#     except Exception as e:
#         return False, f"Error al enviar correo de verificación: {e}"


# --- Funciones CRUD (Crear, Leer, Actualizar, Borrar) para Realtime Database ---
# Estas funciones interactúan con la Realtime Database para almacenar y gestionar
# los datos del perfil de usuario y las transacciones financieras.

def create_user_profile(uid, user_data):
    """
    Crea o actualiza un perfil de usuario en Firebase Realtime Database.
    Utiliza el User ID (UID) de Firebase Authentication como clave principal.

    Args:
        uid (str): El User ID (UID) único del usuario obtenido de Firebase Authentication.
        user_data (dict): Un diccionario con los datos del perfil del usuario
                          (ej. nombre, saldo inicial, fecha de registro).

    Returns:
        tuple: Una tupla conteniendo:
            - bool: True si la operación fue exitosa, False en caso contrario.
            - str: Un mensaje de éxito o un mensaje de error descriptivo.
    """
    try:
        # Accede al nodo 'perfiles_usuarios' y usa el UID como una sub-clave
        # para almacenar los datos del perfil. `.set()` sobrescribe los datos existentes
        # en esa ubicación si el UID ya existe, o los crea si es nuevo.
        db.child("perfiles_usuarios").child(uid).set(user_data)
        return True, f"Perfil para UID '{uid}' creado/actualizado correctamente."
    except Exception as e:
        print(f"Error en create_user_profile: {e}") # Imprime el error para depuración
        return False, f"Error al crear/actualizar perfil para UID '{uid}': {e}"

def get_user_profile(uid):
    """
    Obtiene el perfil de un usuario específico desde Firebase Realtime Database.

    Args:
        uid (str): El User ID (UID) del usuario cuyo perfil se desea obtener.

    Returns:
        tuple: Una tupla conteniendo:
            - dict: Los datos del perfil del usuario si existen, o None si no se encuentra.
            - str: Un mensaje de éxito o un mensaje de error si ocurre un problema.
    """
    try:
        # Obtiene una "snapshot" (captura de datos) del nodo del perfil del usuario.
        profile_snapshot = db.child("perfiles_usuarios").child(uid).get()
        
        # `val()` devuelve los datos del snapshot. Si el nodo no existe, devuelve None.
        if profile_snapshot.val():
            return profile_snapshot.val(), None # Devuelve los datos del perfil y None para el error
        else:
            return None, f"No se encontró perfil para UID '{uid}'."
    except Exception as e:
        print(f"Error en get_user_profile: {e}") # Imprime el error para depuración
        return None, f"Error al obtener perfil para UID '{uid}': {e}"

def add_transaction(uid, transaction_data):
    """
    Agrega una nueva transacción para un usuario específico en Realtime Database.
    Utiliza `push()` para generar una clave única para cada transacción,
    asegurando que las transacciones no se sobrescriban.

    Args:
        uid (str): El User ID (UID) del usuario al que pertenece la transacción.
        transaction_data (dict): Un diccionario con los detalles de la transacción
                                 (ej. monto, descripción, fecha, categoría, tipo).

    Returns:
        tuple: Una tupla conteniendo:
            - str: La clave única generada para la transacción si tiene éxito, o None si falla.
            - str: Un mensaje de éxito o un mensaje de error descriptivo.
    """
    try:
        # Accede al nodo 'transacciones' y al sub-nodo con el UID del usuario.
        # `.push(transaction_data)` agrega los datos bajo una clave generada automáticamente.
        new_transaction_ref = db.child("transacciones").child(uid).push(transaction_data)
        
        # 'name' contiene la clave única (ID) que Firebase generó para esta nueva transacción.
        transaction_key = new_transaction_ref['name']
        return transaction_key, f"Transacción agregada con éxito (Clave: {transaction_key})."
    except Exception as e:
        print(f"Error en add_transaction: {e}") # Imprime el error para depuración
        return None, f"Error al agregar transacción para UID '{uid}': {e}"

def get_transactions(uid):
    """
    Obtiene todas las transacciones registradas para un usuario específico.

    Args:
        uid (str): El User ID (UID) del usuario cuyas transacciones se desean obtener.

    Returns:
        tuple: Una tupla conteniendo:
            - dict: Un diccionario donde las claves son los IDs de transacción
                    y los valores son los datos de la transacción,
                    o un diccionario vacío `{}` si no hay transacciones.
            - str: Un mensaje de éxito o un mensaje de error si ocurre un problema.
    """
    try:
        # Obtiene una snapshot de todas las transacciones bajo el UID del usuario.
        transactions_snapshot = db.child("transacciones").child(uid).get()
        
        if transactions_snapshot.val():
            return transactions_snapshot.val(), None # Devuelve el dict de transacciones y None para el error
        else:
            # Si no hay transacciones, devuelve un diccionario vacío para indicar que no hay datos.
            return {}, None # Devuelve un dict vacío y None para el error
    except Exception as e:
        print(f"Error en get_transactions: {e}") # Imprime el error para depuración
        return None, f"Error al obtener transacciones para UID '{uid}': {e}"

def update_transaction(uid, transaction_key, updates):
    """
    Actualiza los detalles de una transacción específica para un usuario.

    Args:
        uid (str): El User ID (UID) del usuario.
        transaction_key (str): La clave única (ID) de la transacción a actualizar.
        updates (dict): Un diccionario con los campos a actualizar y sus nuevos valores.
                        Solo los campos presentes en este diccionario serán modificados.

    Returns:
        tuple: Una tupla conteniendo:
            - bool: True si la actualización fue exitosa, False en caso contrario.
            - str: Un mensaje de éxito o un mensaje de error descriptivo.
    """
    try:
        # Navega hasta la transacción específica usando el UID y la clave de transacción.
        # `.update(updates)` actualiza solo los campos especificados en el diccionario `updates`.
        db.child("transacciones").child(uid).child(transaction_key).update(updates)
        return True, f"Transacción '{transaction_key}' actualizada para UID '{uid}'."
    except Exception as e:
        print(f"Error en update_transaction: {e}") # Imprime el error para depuración
        return False, f"Error al actualizar transacción '{transaction_key}' para UID '{uid}': {e}"

def delete_transaction(uid, transaction_key):
    """
    Elimina una transacción específica para un usuario de la Realtime Database.

    Args:
        uid (str): El User ID (UID) del usuario.
        transaction_key (str): La clave única (ID) de la transacción a eliminar.

    Returns:
        tuple: Una tupla conteniendo:
            - bool: True si la eliminación fue exitosa, False en caso contrario.
            - str: Un mensaje de éxito o un mensaje de error descriptivo.
    """
    try:
        # Navega hasta la transacción específica y la elimina usando `.remove()`.
        db.child("transacciones").child(uid).child(transaction_key).remove()
        return True, f"Transacción '{transaction_key}' eliminada para UID '{uid}'."
    except Exception as e:
        print(f"Error en delete_transaction: {e}") # Imprime el error para depuración
        return False, f"Error al eliminar transacción '{transaction_key}' para UID '{uid}': {e}"