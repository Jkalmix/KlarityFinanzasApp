# ===========================================================================================
# firebase_service.py
# -------------------------------------------------------------------------------------------
# Módulo encargado de:
# - Inicializar la conexión con Firebase (cliente Pyrebase + Admin SDK).
# - Proveer funciones CRUD para:
#     • Usuarios (registro, login).
#     • Perfil (nombre, foto).
#     • Categorías (ingresos/gastos).
#     • Transacciones.
#     • Sugerencias generadas por IA.
#     • Cambio de contraseña seguro.
# ===========================================================================================

import os
import sys
import time
from typing import Tuple, Optional, Dict

import pyrebase                      # Cliente Python para Firebase (Auth + Realtime DB).
import firebase_admin                # SDK de administrador para Firebase.
from firebase_admin import credentials, auth as admin_auth

# -------------------------------------------------------------------------------------------
# 1) Configuración del path para importar archivos en 'config/'
# -------------------------------------------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
config_dir = os.path.join(current_dir, '..', 'config')
if config_dir not in sys.path:
    sys.path.append(config_dir)      # Añade la carpeta config al path

from firebase_config import FIREBASE_CONFIG, SERVICE_ACCOUNT_KEY_PATH

# -------------------------------------------------------------------------------------------
# 2) Inicialización de Firebase
# -------------------------------------------------------------------------------------------
# Pyrebase4: para que el usuario "normal" haga login, registro y CRUD en DB.
firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
auth = firebase.auth()               # Módulo de autenticación (email/password, etc.).
db = firebase.database()             # Cliente para Realtime Database.

# Admin SDK: para operaciones que requieren privilegios elevados,
# como cambiar contraseñas directamente desde el servidor.
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
    firebase_admin.initialize_app(cred)

# -------------------------------------------------------------------------------------------
# 3) FUNCIONES DE AUTENTICACIÓN
# -------------------------------------------------------------------------------------------

def register_user(email: str, password: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Crea un usuario nuevo en Firebase Authentication.
    - email: correo del usuario.
    - password: clave que debe tener mínimo 6 caracteres.
    Retorna (user_dict, None) si OK, o (None, error_msg) si falla.
    """
    try:
        user = auth.create_user_with_email_and_password(email, password)
        return user, None
    except Exception as e:
        return None, str(e)

def login_user(email: str, password: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Inicia sesión con email y password.
    - Si las credenciales son válidas, retorna (user_dict, None).
    - Si falla, retorna (None, mensaje_amigable).
    """
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return user, None
    except Exception as e:
        msg = str(e)
        # Interceptamos errores comunes y devolvemos mensajes en español
        if "INVALID_LOGIN_CREDENTIALS" in msg or "Invalid password" in msg:
            friendly = "Usuario o contraseña incorrectos."
        else:
            friendly = "Error al iniciar sesión. Por favor, inténtalo de nuevo."
        return None, friendly

# -------------------------------------------------------------------------------------------
# 4) FUNCIONES DE PERFIL
# -------------------------------------------------------------------------------------------

def create_or_update_profile(uid: str, data: dict) -> Tuple[bool, Optional[str]]:
    """
    Guarda o actualiza los datos del perfil de usuario en Realtime DB.
    - uid: identificador único del usuario.
    - data: dict con campos a actualizar (nombre, foto, email, etc.).
    Retorna (True, None) si OK, o (False, error_msg) si falla.
    """
    try:
        db.child("usuarios").child(uid).update(data)
        return True, None
    except Exception as e:
        return False, str(e)

def get_profile(uid: str) -> Tuple[Dict, Optional[str]]:
    """
    Recupera el perfil completo de un usuario.
    - Retorna ({...campos...}, None) si OK, o ({}, error_msg) si falla.
    """
    try:
        snap = db.child("usuarios").child(uid).get()
        return snap.val() or {}, None
    except Exception as e:
        return {}, str(e)

# -------------------------------------------------------------------------------------------
# 5) CRUD DE CATEGORÍAS
# -------------------------------------------------------------------------------------------

def add_category(uid: str, data: dict) -> Tuple[Optional[str], Optional[str]]:
    """
    Agrega una nueva categoría (por ejemplo, "Alimentos", tipo "Gasto").
    Retorna (new_key, None) si OK, o (None, error_msg) si falla.
    """
    try:
        key = db.child("categorias").child(uid).push(data)["name"]
        return key, None
    except Exception as e:
        return None, str(e)

def get_categories(uid: str) -> Tuple[Dict, Optional[str]]:
    """
    Obtiene todas las categorías de un usuario, en formato {key: datos}.
    """
    try:
        snap = db.child("categorias").child(uid).get()
        return snap.val() or {}, None
    except Exception as e:
        return {}, str(e)

def update_category(uid: str, key: str, updates: dict) -> Tuple[bool, Optional[str]]:
    """
    Actualiza una categoría específica (por ejemplo, renombrar).
    """
    try:
        db.child("categorias").child(uid).child(key).update(updates)
        return True, None
    except Exception as e:
        return False, str(e)

def delete_category(uid: str, key: str) -> Tuple[bool, Optional[str]]:
    """
    Elimina una categoría por su key.
    """
    try:
        db.child("categorias").child(uid).child(key).remove()
        return True, None
    except Exception as e:
        return False, str(e)

# -------------------------------------------------------------------------------------------
# 6) CRUD DE TRANSACCIONES
# -------------------------------------------------------------------------------------------

def add_transaction(uid: str, data: dict) -> Tuple[Optional[str], Optional[str]]:
    """
    Inserta una nueva transacción (ej. 2025-07-13, monto 15000, tipo "Gasto").
    Retorna (trans_key, None) o (None, error_msg).
    """
    try:
        key = db.child("transacciones").child(uid).push(data)["name"]
        return key, None
    except Exception as e:
        return None, str(e)

def get_transactions(uid: str) -> Tuple[Dict, Optional[str]]:
    """
    Recupera todas las transacciones de un usuario.
    """
    try:
        snap = db.child("transacciones").child(uid).get()
        return snap.val() or {}, None
    except Exception as e:
        return {}, str(e)

def get_single_transaction(uid: str, key: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Recupera una única transacción por su key.
    """
    try:
        snap = db.child("transacciones").child(uid).child(key).get()
        return snap.val() or None, None
    except Exception as e:
        return None, str(e)

def update_transaction(uid: str, key: str, updates: dict) -> Tuple[bool, Optional[str]]:
    """
    Modifica campos de una transacción existente.
    """
    try:
        db.child("transacciones").child(uid).child(key).update(updates)
        return True, None
    except Exception as e:
        return False, str(e)

def delete_transaction(uid: str, key: str) -> Tuple[bool, Optional[str]]:
    """
    Elimina una transacción por su key.
    """
    try:
        db.child("transacciones").child(uid).child(key).remove()
        return True, None
    except Exception as e:
        return False, str(e)

# -------------------------------------------------------------------------------------------
# 7) SUGERENCIAS DE IA (historial)
# -------------------------------------------------------------------------------------------

def save_ai_suggestion(uid: str, text: str) -> None:
    """
    Guarda el texto generado por Gemini en /ai_sugerencias/{uid}/{timestamp}.
    Esto permite llevar un historial de todas las recomendaciones.
    """
    ts = int(time.time())  # timestamp en segundos
    db.child("ai_sugerencias").child(uid).child(str(ts)).set({
        "texto": text,
        "ts": ts
    })

def get_ai_suggestions(uid: str) -> Tuple[Dict, Optional[str]]:
    """
    Recupera todas las sugerencias guardadas del usuario.
    """
    try:
        snap = db.child("ai_sugerencias").child(uid).get()
        return snap.val() or {}, None
    except Exception as e:
        return {}, str(e)

def delete_ai_suggestion(uid: str, ts: int) -> Tuple[bool, Optional[str]]:
    """
    Elimina una sugerencia específica usando su timestamp (clave).
    """
    try:
        db.child("ai_sugerencias").child(uid).child(str(ts)).remove()
        return True, None
    except Exception as e:
        return False, str(e)

# -------------------------------------------------------------------------------------------
# 8) CATEGORÍAS POR DEFECTO AL REGISTRAR USUARIO
# -------------------------------------------------------------------------------------------
from constants import DEFAULT_CATEGORIES

def ensure_default_categories(uid: str) -> None:
    """
    Revisa si el usuario ya tiene categorías; si no, crea las definidas en DEFAULT_CATEGORIES.
    Esto se llama al hacer login por primera vez tras un registro.
    """
    cats, _ = get_categories(uid)
    if cats:
        return
    for cat in DEFAULT_CATEGORIES:
        add_category(uid, cat)

# -------------------------------------------------------------------------------------------
# 9) CAMBIO DE CONTRASEÑA SEGURO
# -------------------------------------------------------------------------------------------

def reauthenticate_user(email: str, password: str) -> Tuple[bool, Optional[str]]:
    """
    Antes de cambiar la contraseña, reautentica con la contraseña actual.
    Retorna (True, None) si OK, o (False, mensaje_amigable) si falla.
    """
    try:
        auth.sign_in_with_email_and_password(email, password)
        return True, None
    except Exception as e:
        msg = str(e)
        if "INVALID_LOGIN_CREDENTIALS" in msg or "Invalid password" in msg:
            return False, "Contraseña actual incorrecta."
        return False, "Error de autenticación."

def update_password(user_or_uid, new_password: str) -> Tuple[bool, Optional[str]]:
    """
    Cambia la contraseña del usuario utilizando Firebase Admin SDK.
    user_or_uid puede ser:
      - un dict de usuario (con 'localId'),
      - o el uid directamente.
    """
    try:
        uid = user_or_uid['localId'] if isinstance(user_or_uid, dict) else user_or_uid
        admin_auth.update_user(uid, password=new_password)
        return True, None
    except Exception as e:
        return False, str(e)
