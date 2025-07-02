# KlarityFinanzasApp

¡Bienvenido/a a KlarityFinanzasApp! Una aplicación de escritorio para la gestión personal de finanzas, construida con Python y Tkinter, y potenciada por Firebase para autenticación y almacenamiento de datos.

## 🚀 Características Principales (hasta ahora)

* **Autenticación de Usuarios:**
    * Registro de nuevos usuarios con email y contraseña (gestionado por Firebase Authentication).
    * Inicio de sesión para usuarios existentes (gestionado por Firebase Authentication).
    * Validación básica de campos y contraseñas.
    * Manejo de errores específicos de Firebase (ej. email ya registrado, contraseña débil, usuario no encontrado).

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
* **Python 3.12.4**
* **Tkinter:** Para la interfaz gráfica de usuario.
* **Pillow (PIL):** Para el manejo de imágenes (ej. logos).
* **Pyrebase4:** Para interactuar con Firebase Authentication y Realtime Database.

## 📦 Estructura del Proyecto

KLARITYFINANZASAPP/
├── .venv/                     # Entorno virtual de Python
├── assets/
│   └── klarity_logo.png       # Logo de la aplicación
├── config/
│   ├── firebase_config.py     # Configuración de Firebase API y credenciales
│   └── klarityfinanzasapp-firebase-adminsdk-fbsvc-592c154bdf.json # Clave de servicio de Firebase Admin SDK
├── docs/           
│   ├── logo_slogan_justification.md
│   └── palette_justification.md
├── src/
│   ├── firebase_service.py    # Módulo con todas las funciones de interacción con Firebase
│   ├── main.py                # Lógica principal de la aplicación y la GUI
│   └── splash_screen.py       # (Si lo usas) Pantalla de carga inicial
│   └── test_firebase_connection.py # (Si existe) Script para probar la conexión a Firebase
└── README.md                  # Este archivo



## ⚙️ Configuración y Ejecución
1. Configuración del Entorno Virtual en VS Code
Es crucial que Visual Studio Code use el entorno virtual de tu proyecto para aislar las dependencias.

Abrir la Paleta de Comandos:
Dentro de VS Code, presiona Ctrl + Shift + P (Windows/Linux) o Cmd + Shift + P (macOS).
Seleccionar el Intérprete de Python:
En la barra de comandos que aparece, escribe Python: Select Interpreter (o Python: Seleccionar Intérprete).
Selecciona esta opción.
VS Code intentará detectar los entornos. Deberías ver una opción que se parezca a Python 3.x.x (.venv) o Python 3.x.x (Environment) que apunta a tu carpeta .venv dentro de KLARITYFINANZASAPP.
Selecciónala.
Si no la ves, o solo ves intérpretes globales, haz lo siguiente:
Selecciona Enter interpreter path... (Introducir ruta del intérprete...).
Luego, selecciona Find... (Buscar...).
Navega a tu carpeta KLARITYFINANZASAPP > .venv > Scripts (en Windows) o bin (en macOS/Linux).
Selecciona el archivo python.exe (en Windows) o python (en macOS/Linux) dentro de esa carpeta.
Verificar Intérprete Activo:
Una vez seleccionado, en la barra de estado inferior de VS Code (normalmente en la esquina inferior izquierda), deberías ver el nombre del intérprete actual, por ejemplo: Python 3.x.x (.venv). Esto confirma que VS Code está usando tu entorno virtual.
1. Instalación de Librerías (Dependencias)
Aunque hayas copiado la carpeta .venv, es posible que las librerías no sean compatibles si la versión de Python del nuevo PC es muy diferente, o si el entorno virtual se corrompió durante la copia. La mejor práctica es verificar o reinstalarlas.

Abrir la Terminal Integrada de VS Code:
Ve a Terminal > New Terminal (o Terminal > Nueva Terminal).
Verás que la terminal se abre y automáticamente activa tu entorno virtual (deberías ver (.venv) al principio de la línea de comandos).
Instalar las Librerías:
En esta terminal, ejecuta el siguiente comando para asegurarte de que todas las dependencias están instaladas:
Bash

pip install Pyrebase4 Pillow


1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/jkalmix/KlarityFinanzasApp.git](https://github.com/jkalmix/KlarityFinanzasApp.git)
    cd KlarityFinanzasApp
    ```

2.  **Configurar Entorno Virtual (Recomendado):**
    ```bash
    python -m venv .venv
    # En Windows:
    .venv\Scripts\activate
    # En macOS/Linux:
    source .venv/bin/activate
    ```

3.  **Instalar Dependencias:**
    ```bash
    pip install tkinter Pillow pyrebase4
    ```

4.  **Configurar Firebase:**
    * Crea un nuevo proyecto en [Firebase Console](https://console.firebase.google.com/).
    * **Habilita el método de inicio de sesión "Email/Password"** en Authentication -> Sign-in method.
    * **Crea una aplicación web** en tu proyecto Firebase y copia las credenciales de configuración.
    * Crea el archivo `config/firebase_config.py` y pega tus credenciales:
        ```python
        # config/firebase_config.py
        import os
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        SERVICE_ACCOUNT_KEY_PATH = os.path.join(BASE_DIR, 'archivo.json')

        FIREBASE_CONFIG = {
            "apiKey": "TU_API_KEY_AQUI",
            "authDomain": "tu-proyecto.firebaseapp.com",
            "databaseURL": "[https://tu-proyecto-default-rtdb.firebaseio.com](https://tu-proyecto-default-rtdb.firebaseio.com)",
            "projectId": "tu-project-id",
            "storageBucket": "tu-project-id.appspot.com",
            "messagingSenderId": "TU_SENDER_ID_AQUI",
            "appId": "TU_APP_ID_AQUI",
        }
        ```
    * Descarga el **archivo JSON de la cuenta de servicio** desde Firebase Console (Project settings -> Service accounts -> Generate new private key) y guárdalo como `klarityfinanzasapp-firebase-adminsdk-fbsvc-592c154bdf.json` **dentro de la carpeta `config/`**.

5.  **Ejecutar la Aplicación:**
    ```bash
    python src/main.py
    ```
