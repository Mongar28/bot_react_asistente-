from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from rag.split_docs import load_split_docs
from rag.llm import load_llm_openai
from rag.embeddings import load_embeddins
from rag.retriever import create_retriever
from rag.vectorstore import create_verctorstore
from rag.rag_chain import create_rag_chain
from datetime import datetime
import pytz
import telebot
import os


class LangChainTools:
    def load_llm_openai(self):
        load_dotenv()
        # model = "gpt-3.5-turbo-0125"
        # model = "gpt-4o"
        model = "gpt-4o-mini"

        llm = ChatOpenAI(
            model=model,
            temperature=0.0,
            max_tokens=2000,
        )
        return llm


@tool
def redact_email(topic: str) -> str:
    """Use this tool to draft the content of an email based on a topic."""

    # Load LLM model
    langChainTools = LangChainTools()

    llm = langChainTools.load_llm_openai()
    # Create prompt for the LLM
    prompt = (
        "Please redact a email based on the topic:\n\n"
        "Topic: {}\n\n"
        "Email Content: [Your email content here]"
    ).format(topic)

    response = llm.invoke(prompt)
    return response


@tool
def list_calendar_events(max_results: int = 50) -> list:
    """Use this tool to list upcoming calendar events."""

    # Define los alcances que necesitamos para acceder a la API de Google Calendar
    SCOPES = ['https://www.googleapis.com/auth/calendar']

    creds = None

    # La ruta al archivo token.json, que contiene los tokens de acceso y actualización
    token_path = 'token_2.json'

    # La ruta al archivo de credenciales de OAuth 2.1
    creds_path = 'credentials_2.json'

    # Cargar las credenciales desde el archivo token.json, si existe
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # Si no hay credenciales válidas disponibles, inicia el flujo de OAuth 2.0 para obtener nuevas credenciales
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Guarda las credenciales para la próxima ejecución
        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())

    # Construye el objeto de servicio para interactuar con la API de Google Calendar
    service = build('calendar', 'v3', credentials=creds)

    # Identificador del calendario que deseas consultar. 'primary' se refiere al calendario principal del usuario.
    calendar_id = 'primary'

    # Realiza una llamada a la API para obtener una lista de eventos.
    now = datetime.now(timezone.utc).isoformat()  # 'Z' indica UTC
    events_result = service.events().list(
        calendarId=calendar_id, timeMin=now, maxResults=max_results, singleEvents=True,
        orderBy='startTime').execute()

    # Extrae los eventos de la respuesta de la API.
    events = events_result.get('items', [])

    # Si no se encuentran eventos, imprime un mensaje.
    if not events:
        print('No upcoming events found.')
        return

    # Recorre la lista de eventos y muestra la hora de inicio y el resumen de cada evento.
    for event in events:
        # Obtiene la fecha y hora de inicio del evento. Puede ser 'dateTime' o 'date'.
        start = event['start'].get('dateTime', event['start'].get('date'))
        # Imprime la hora de inicio y el resumen (título) del evento.
        print(start, event['summary'])

    return events


@tool
def create_calendar_event(
        title: str, start_time: datetime,
        end_time: datetime, attendees: list) -> dict:
    """Use this tool to create an event in the calendar.

    Parameters:
    - title: str - The title of the event.
    - start_time: datetime - The start time of the event.
    - end_time: datetime - The end time of the event.
    - attendees: list - A list of attendee emails (required).

    Returns:
    - dict - The created event details.
    """

    if not attendees:
        raise ValueError(
            "El campo 'attendees' es obligatorio y no puede estar vacío.")

    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = None

    # La ruta al archivo token.json, que contiene los tokens de acceso y actualización
    token_path = 'token_2.json'

    # La ruta al archivo de credenciales de OAuth 2.0
    creds_path = 'credentials_2.json'

    # Cargar las credenciales desde el archivo token.json, si existe
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # Si no hay credenciales válidas disponibles, inicia el flujo de OAuth 2.0 para obtener nuevas credenciales
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Guarda las credenciales para la próxima ejecución
        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())

    # Construye el objeto de servicio para interactuar con la API de Google Calendar
    service = build('calendar', 'v3', credentials=creds)

    # Validar y filtrar asistentes
    valid_attendees = []
    for email in attendees:
        if isinstance(email, str) and '@' in email:
            valid_attendees.append({'email': email})
        else:
            raise ValueError(f"'{email}' no es un correo electrónico válido.")

    # Identificador del calendario que deseas modificar. 'primary' se refiere al calendario principal del usuario.
    calendar_id = 'primary'

    # Define el cuerpo del evento con el título, la hora de inicio y la hora de finalización
    event = {
        'summary': title,
        'start': {
            'dateTime': start_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'timeZone': 'America/Bogota',
        },
        'end': {
            'dateTime': end_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'timeZone': 'America/Bogota',
        },
        'attendees': valid_attendees
    }

    try:
        # Crea el evento en el calendario
        event = service.events().insert(calendarId=calendar_id, body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))
    except Exception as e:
        print(f"Error al crear el evento: {e}")
        return {}

    return event


@tool
def create_quick_add_event(quick_add_text: str):
    """Use this tool to create events in the calendar from natural language, 
    using the Quick Add feature of Google Calendar.
    """
    quick_add_text: str = input(
        "- Escribe la descripcion del evento que quieres crear: ")
    SCOPES = ['https://www.googleapis.com/auth/calendar']

    creds = None

    # La ruta al archivo token.json, que contiene los tokens de acceso y actualización
    token_path = 'token_2.json'

    # La ruta al archivo de credenciales de OAuth 2.0
    creds_path = 'credentials_2.json'

    # Cargar las credenciales desde el archivo token.json, si existe
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # Si no hay credenciales válidas disponibles, inicia el flujo de OAuth 2.0 para obtener nuevas credenciales
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Guarda las credenciales para la próxima ejecución
        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())

    # Construye el objeto de servicio para interactuar con la API de Google Calendar
    service = build('calendar', 'v3', credentials=creds)

    # Identificador del calendario que deseas modificar. 'primary' se refiere al calendario principal del usuario.
    calendar_id = 'primary'

    # Crea el evento utilizando la funcionalidad Quick Add
    event = service.events().quickAdd(
        calendarId=calendar_id, text=quick_add_text).execute()

    print('Event created: %s' % (event.get('htmlLink')))

    return event


# @tool
# def send_message(message: str):
#     """Use this function when you need to communicate with the user."""
#     # Configuración del bot
#     load_dotenv()
#     API_TOKEN_BOT = os.getenv("API_TOKEN_BOT")
#     bot = telebot.TeleBot(API_TOKEN_BOT)
#
#     bot.send_message(chat_id="5076346205", text=message)
#

@tool
def send_message(message: str):
    """Use this function when you need to communicate with Cristian."""
    # Configuración del bot
    load_dotenv()
    API_TOKEN_BOT = os.getenv("API_TOKEN_BOT")
    bot = telebot.TeleBot(API_TOKEN_BOT)

    # Escapar caracteres especiales en Markdown
    from telebot.util import escape_markdown
    safe_message = escape_markdown(message)

    # Enviar mensaje usando MarkdownV2
    bot.send_message(chat_id="5076346205", text=safe_message,
                     parse_mode="Markdown")


@tool
def get_vitae_info(prompt: str) -> str:
    """Use this function when you need more information about Cristian Montoya Garcés."""
    file_path: str = 'hoja_vida_cristian.pdf'

    docs_split: list = load_split_docs(file_path)
    embeddings_model = load_embeddins()
    llm = load_llm_openai()
    create_verctorstore(
        docs_split,
        embeddings_model,
        file_path
    )
    retriever = create_retriever(
        embeddings_model,
        persist_directory="embeddings/hoja_vida_cristian"
    )
    qa = create_rag_chain(
        llm, retriever)

    # prompt: str = "Escribe un parrarfo describiendo cuantos son y  cuales son los servicios que ofrece OneCluster y brinda detalles sobre cada uno."
    response = qa.invoke(
        {"input": prompt, "chat_history": []}
    )

    return response["answer"]


@tool
def get_current_date_and_time():
    """
    Use this function when you need to know the current date and time.

    Returns:
        str: Current date and time in Bogotá, Colombia.
    """
    bogota_tz = pytz.timezone('America/Bogota')
    current_date_and_time = datetime.now(bogota_tz)
    return current_date_and_time.strftime('%Y-%m-%d %H:%M:%S')
