# EZMessage

**EZMessage es una app de mensajería de código abierto, 100% privada y local, construida sobre Python.**

---

## 🔒 ¿Cómo funcionan los datos y los chats?
Todo se gestiona de forma **estrictamente local** en tu equipo. La aplicación no envía tus conversaciones ni credenciales a servidores externos.

Al ejecutar el programa, se crean de forma automática los siguientes archivos en la misma carpeta:
* `david_accounts.json`: Almacena los perfiles de usuario locales.
* `ezmessage_chats.json`: Guarda el historial completo de tus mensajes.
* `ezmessage_config.json`: Registra tus preferencias de Inteligencia Artificial.

---

## 🔑 ¿Se puede iniciar sesión con Google y Apple?
**Sí, pero el flujo es simulado a nivel local**. Funciona como un inicio de sesión *OAuth offline*: el programa solicita tu correo electrónico únicamente para generar o vincular una Cuenta David interna. No se conecta a las APIs oficiales de Google o Apple ni requiere contraseñas en red.

---

## 👥 ¿Qué hago si no tengo contactos en mi equipo?
Puedes iniciar un chat seleccionando **"Nueva conversación"** e ingresando el nombre de usuario de otra cuenta creada en tu misma máquina. 

Si quieres probar la app a solas, la mejor solución es chatear con Inteligencias Artificiales pulsando el botón **"🤖 Asistente AI"**.

### 🛠️ Configuración del Asistente AI (EZPack AI)
El asistente se ejecuta en tu navegador web. Tienes dos formas de configurarlo:
* **Opción Local:** Descarga el archivo `ezpack.html` de este repositorio y colócalo en la misma carpeta de `EZMessage`. Al presionar **"Asistente AI"**, se abrirá la interfaz local.
* **Opción Externa:** Haz clic en el botón de configuración (los tres puntos `⋯`), elige **"Configurar IA…"** y selecciona el proveedor de tu preferencia (ChatGPT, Gemini, Claude, DeepSeek, Grok). Luego, desde el menú, puedes seleccionar **"Abrir [Proveedor] en el navegador"**.

---

## 📋 Requisitos del Sistema
* [Python 3.14+](https://python.org) [1]
* **Tkinter** (Librería nativa de interfaz gráfica, incluida por defecto en la instalación estándar de Python).

---

## 🔄 Alternativas de Mensajería
Si deseas evaluar o comparar el uso de este proyecto frente a servicios comerciales en la nube:
* [WhatsApp](https://whatsapp.com)
* [Telegram](https://telegram.org)
* [Messenger](https://messenger.com)
* [Facebook](https://facebook.com)
* [Google Messages](https://google.com)

---

<p align="center">
  <b>Hecho en Python 3.14. Si te gustó el proyecto, ¡apóyanos dejándole una estrella ⭐ al repositorio!</b>
</p>
