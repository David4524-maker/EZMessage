# EZMessage 💬🤖
> **Mensajería local interactiva con Cuentas David y asistente EZPack AI.**

EZMessage es una aplicación de mensajería de escritorio construida en Python (Tkinter). Permite a los usuarios de un mismo equipo comunicarse entre sí de forma privada a través de "Cuentas David", además de ofrecer una integración directa con múltiples proveedores de Inteligencia Artificial (ChatGPT, Gemini, Claude, DeepSeek, Grok) mediante **EZPack AI**.

---

## ✨ Características Principales

*   **Sistema de Cuentas David:** Crea cuentas de usuario de manera local. Soporta dos modalidades:
    *   *Uso normal:* Con correo electrónico y sin límite de edad.
    *   *Cuenta Infantil:* Diseñada para niños/as (1-17 años), sin requerir correo electrónico y con indicadores visuales dedicados.
*   **Chat Local en Tiempo Real:** Envía y recibe mensajes al instante entre las cuentas registradas en el mismo ordenador. Incluye confirmaciones de lectura (✓✓), marcas de tiempo y vista previa de mensajes no leídos.
*   **Interfaz Gráfica Moderna (Dark Mode):** Interfaz fluida y atractiva construida con Tkinter, sin necesidad de librerías externas complejas. Incluye avatares generados automáticamente según el nombre, scroll suave y diseño *responsive*.
*   **🤖 EZPack AI Integrado:** Pulsa un botón para desplegar tu asistente de Inteligencia Artificial en el navegador. Puedes configurar y alternar fácilmente entre:
    *   EZPack Local (Offline)
    *   ChatGPT
    *   Gemini
    *   Claude
    *   DeepSeek
    *   Grok
*   **Privacidad Local:** Todos los datos (cuentas, mensajes y configuraciones) se guardan en archivos `.json` locales en la misma carpeta del programa. Nada va a servidores externos de mensajería.

---

## 📋 Requisitos Previos

Para ejecutar EZMessage necesitas:
*   **Python 3.x** instalado en tu sistema (probado en Python 3.8+).
*   El archivo principal del código: `ezmessage.py`.
*   El archivo del asistente virtual: **`ezpack.html`** (debe estar en la misma carpeta que el script de Python).

*Nota: No requiere instalar dependencias adicionales vía `pip`, ya que utiliza las bibliotecas estándar de Python (`tkinter`, `json`, `hashlib`, `webbrowser`, etc.).*

---

## 🚀 Instalación y Uso

1. **Clona o descarga** este repositorio en tu ordenador:
   ```bash
   git clone https://github.com/tu-usuario/ezmessage.git
   cd ezmessage
   ```
2. **Asegúrate** de que el archivo `ezpack.html` se encuentre en el mismo directorio.
3. **Ejecuta la aplicación**:
   Puedes hacer doble clic en el archivo `ezmessage.py`, o bien ejecutarlo desde la terminal:
   ```bash
   python ezmessage.py
   ```
   *(También puedes abrirlo en IDLE y pulsar F5).*
4. **Crea tu primera Cuenta David** desde la pantalla de inicio, inicia sesión ¡y comienza a chatear!

---

## 📂 Estructura de Archivos

Al usar la aplicación, se generarán automáticamente los siguientes archivos de datos en la misma carpeta:

| Archivo | Descripción |
| :--- | :--- |
| `ezmessage.py` | El script principal de la aplicación. |
| `ezpack.html` | Interfaz web del asistente de IA (Requisito). |
| `david_accounts.json` | Almacena los usuarios, contraseñas encriptadas (SHA-256) y perfiles. |
| `ezmessage_chats.json` | Contiene el historial completo de los chats locales. |
| `ezmessage_config.json` | Guarda tus preferencias (ej. qué proveedor de IA usas). |

---

## 🛠️ Personalización de la IA

Para cambiar el proveedor de Inteligencia Artificial:
1. Inicia sesión con tu Cuenta David.
2. Abre el menú lateral pulsando en el botón **( ⋯ )** junto a tu nombre.
3. Selecciona **"⚙️ Configurar IA..."** y elige tu plataforma favorita.
4. Al hacer clic en el botón verde **"🤖 Asistente AI"**, EZPack se abrirá en tu navegador web configurado con tu elección.

---

## 📄 Licencia

Este proyecto es de código abierto. Siéntete libre de modificarlo, mejorarlo o usarlo como base para tus proyectos de interfaces gráficas en Python.