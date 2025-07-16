# KlarityFinanzasApp

**KlarityFinanzasApp** es una aplicación de escritorio multiplataforma diseñada para ayudarte a gestionar tus finanzas personales de forma clara, sencilla y segura. Construida con Python y Tkinter, y potenciada por Firebase, ofrece una interfaz intuitiva y herramientas avanzadas para visualizar, categorizar y analizar tus movimientos.

---

## 🚀 Características Principales

1. **Autenticación y Seguridad**

   * Registro de nuevos usuarios y login con email/password (**Firebase Authentication**).
   * Validación de campos, mensajes de error amigables (e.g., email ya registrado, contraseña débil).
   * Cambio de contraseña: re-autenticación y actualización a través del Admin SDK.

* **Gestión de Perfiles de Usuario:**
    * Creación automática de un perfil de usuario inicial en Firebase Realtime Database tras el registro.
    * Almacenamiento de nombre y saldo inicial (aunque el saldo es 0.0 por ahora).

* **Interfaz de Usuario (GUI):**
    * Ventanas dedicadas para Login, Registro y un Dashboard principal.
    * Estilo visual consistente usando Tkinter y `ttk`.
    * Muestra y oculta contraseñas en los campos de entrada.

## 🛠️ Tecnologías Utilizadas
#pip install -r requirements.txt
#pip install firebase_admin
#pip install pillow
#pip install pyrebase4
#pip install firebase
* **Python 3.13**
* **Tkinter:** Para la interfaz gráfica de usuario.
* **Pillow (PIL):** Para el manejo de imágenes (ej. logos).
* **Pyrebase4:** Para interactuar con Firebase Authentication y Realtime Database.

## 📦 Estructura del Proyecto

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

## ⚙️ Requisitos y Setup

1. **Clonar el repositorio**

   ```bash
   git clone https://github.com/jkalmix/KlarityFinanzasApp.git
   cd KlarityFinanzasApp
   ```


2. **Instalar dependencias**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar Firebase**

   * Crear proyecto en [Firebase Console](https://console.firebase.google.com/).
   * Habilitar método Email/Password en Authentication.
   * Generar credenciales de "Web App" y copiar en `config/firebase_config.py`.
   * Descargar JSON de cuenta de servicio y ubicar en `config/`.
4. **Configurar Gemini**
   
  * en la carpeta config se encontrara el archivo gemini_config.pydonde se debe poner la APYKEY de gemini
    
5. **Ejecutar la aplicación**

   ```bash
   python src/main.py
   ```

---
