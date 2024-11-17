# Bot_React_asistente

**Bot_React_asistente** es un proyecto que crea un asistente personal mediante un bot en Telegram, utilizando un agente React de LangChain. Este bot está diseñado para asistir a su usuario realizando diversas tareas, como enviar y revisar correos electrónicos, gestionar citas en Google Calendar, realizar búsquedas en internet y acceder a información de un sistema externo mediante RAG (Recuperación y Generación).

## Funcionalidades

- **Enviar y revisar correos electrónicos** utilizando la API de Gmail.
- **Gestionar citas en Google Calendar**, incluyendo la creación de nuevos eventos y la visualización de eventos existentes.
- **Buscar información en internet** a través de la herramienta TavilySearch.
- **Sistema RAG** para acceder a fuentes de información externas y proporcionar respuestas personalizadas.

Además, el bot tiene la capacidad de procesar mensajes de voz y texto, integrando los modelos de OpenAI para generar respuestas contextuales y dinámicas.

## Requisitos

### Dependencias
Antes de comenzar, asegúrate de instalar las dependencias necesarias. Puedes hacerlo ejecutando:

```bash
pip install -r requirements.txt
```

### Configuración de API

Para que el bot funcione correctamente, necesitarás configurar algunas variables de entorno:

1. **API de OpenAI**: El bot utiliza un modelo LLM de OpenAI (GPT-4 mini), por lo que necesitarás configurar el archivo `.env` con tu clave API de OpenAI.
2. **API de Telegram**: También necesitarás una clave API de Telegram para crear el bot. Añádela en el archivo `.env` como `API_TOKEN_BOT`.
3. **API de Tavily**: El bot utiliza la API de Tavily para realizar búsquedas en internet.

### Archivo `.env`
Crea un archivo `.env` en la raíz de tu proyecto y agrega las siguientes claves:

```
# Claves de configuración del bot
API_TOKEN_BOT="70606ohe7ks"

# Clave API de OpenAI
OPENAI_API_KEY="sk-UKK"

# Clave API de Tavily
TAVILY_API_KEY="tvly-"
```

Asegúrate de reemplazar las claves con las que correspondan a tu cuenta.

### Archivos de configuración
- **`credentials.json` y `token.json`**: Son necesarios para autenticar el acceso a los servicios de Gmail. Asegúrate de tener estos archivos en la raíz del proyecto.

## Estructura del Proyecto

El proyecto utiliza las siguientes tecnologías y herramientas clave:

- **LangChain**: Framework para crear agentes reactivos, utilizando modelos de lenguaje y herramientas de procesamiento de texto.
- **Telegram Bot API**: Para interactuar con los usuarios a través de mensajes de texto y voz.
- **TavilySearch**: Herramienta de búsqueda en internet integrada en el bot.
- **Gmail API**: Utilizada para gestionar correos electrónicos y eventos en el calendario de Google.
- **LangGraph**: Utilizado para crear y gestionar el flujo de interacciones entre los componentes del agente reactivo.

### Archivos clave

- **`react_graph.py.py`**: Contiene la lógica principal del bot, incluyendo el manejo de mensajes de texto y voz.
- **`requirements.txt`**: Lista de dependencias necesarias para ejecutar el proyecto.

## Personalización

1. **Cambiar el nombre del asistente**: Puedes modificar el nombre de la persona a la que debe asistir el bot ajustando el prompt en el archivo `react_graph.py`:
   
   ```python
   system_prompt = ChatPromptTemplate.from_messages(
       [
           ("system", "Tu eres Pancho, el asistente virtual de Cristian Montoya."),
           # Modificar aquí el nombre
       ]
   )
   ```

2. **Ajustar herramientas y servicios**: El bot está configurado para trabajar con herramientas específicas como Gmail y TavilySearch. Puedes agregar o quitar herramientas según las necesidades de tu proyecto.

## Ejecución

Para iniciar el bot, simplemente ejecuta el siguiente comando:

```bash
python  react_graph.py
```

El bot comenzará a escuchar en Telegram y procesará tanto mensajes de texto como mensajes de voz.

## En fase de desarrollo

Este proyecto aún está en fase de experimentación, especialmente en lo que respecta al agente React y al rendimiento del prompt. Se están realizando ajustes y mejoras continuas.

