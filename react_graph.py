from langchain_community.tools.tavily_search import TavilySearchResults
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langchain_tools.agent_tools import (
    redact_email, list_calendar_events,
    create_calendar_event, send_message,
    get_vitae_info, get_current_date_and_time
)
from langchain_community.tools.gmail.utils import (
    build_resource_service, get_gmail_credentials,
)
from langchain_community.agent_toolkits import GmailToolkit
import telebot
from dotenv import load_dotenv
import os
from api_openai.whisper import whisper_api, tts_api
from langchain_tools.agent_tools import LangChainTools
from langchain_core.messages import AIMessage, HumanMessage


load_dotenv()


class State(TypedDict):
    messages: Annotated[list, add_messages]
    is_last_step: bool  # Cambiar a booleano si es necesario


def load_graph():
    # Inicializamos un LLM de OpenAI
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )

    toolkit = GmailToolkit()

    credentials = get_gmail_credentials(
        token_file="token.json",
        scopes=["https://mail.google.com/"],
        client_secrets_file="credentials.json",
    )
    api_resource = build_resource_service(credentials=credentials)
    toolkit = GmailToolkit(api_resource=api_resource)

    tools = toolkit.get_tools()

    search = TavilySearchResults(max_results=2)
    tools.append(search)
    tools.append(redact_email)
    tools.append(list_calendar_events)
    tools.append(create_calendar_event)
    tools.append(get_vitae_info)
    tools.append(get_current_date_and_time)

    system_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Tu eres Pancho, el asistente virtual de Cristian Montoya."),
            ("system", "Debes atender con cordialidad a todas sus solicitudes."),
            ("system", "Siempre dirígete a él siempre por su nombre."),
            ("system", "Si requieres más información para responder, debes solicitársela."),
            ("system", "Antes de crear un evento en calendario o enviar un correo, debes buscar la fecha y hora actual para entender el contexto en tiempo real."),
            ("system", "Antes de enviar un correo o crear un evento debes mostrar los detalles para que el usuario confirme la ejecución de la tarea."),
            ("placeholder", "{messages}"),
        ]
    )

    graph = create_react_agent(
        model=llm, tools=tools, state_schema=State,
        state_modifier=system_prompt,
        checkpointer=MemorySaver()
    )
    return graph


config = {"configurable": {"thread_id": "thread-1", "recursion_limit": 50}}

graph = load_graph()

### ________________ Implementación con el bot ______________________ ###

API_TOKEN_BOT = os.getenv("API_TOKEN_BOT")
bot = telebot.TeleBot(API_TOKEN_BOT)

# Handle '/start' and '/help'
wellcome = "¡Bienvenido! ¿Cómo puedo ayudarte?"


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, wellcome, parse_mode="Markdown")


# Creamos una lista para el historial fuera de las funciones
history = []


@bot.message_handler(content_types=["text", "voice"])
def bot_mensajes(message):
    global history  # Para acceder a la variable global 'history'

    # Si el mensaje es una nota de voz
    if message.voice:
        user_name = message.from_user.first_name
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_path = "audios/nota_de_voz.ogg"

        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        pregunta_usuario = whisper_api(file_path)
        print(f"Pregunta del usuario: {pregunta_usuario}")
        langChainTools = LangChainTools()
        llm = langChainTools.load_llm_openai()

        events = graph.stream(
            {"messages": [("user", pregunta_usuario)],
             "is_last_step": False},
            config, stream_mode="updates"
        )

        for event in events:
            if "agent" in event:
                respuesta_agente = event["agent"]["messages"][-1].content

                # Verificar si la respuesta no está vacía
                if respuesta_agente:
                    bot.send_message(
                        message.chat.id, respuesta_agente,
                        parse_mode="Markdown"
                    )

                    path_voice: str = tts_api(respuesta_agente)
                    with open(path_voice, 'rb') as voice:
                        bot.send_voice(message.chat.id, voice=voice)

                    history.append(HumanMessage(content=pregunta_usuario))
                    history.append(AIMessage(content=respuesta_agente))

    # Si el mensaje es de texto
    if message.text:
        pregunta_usuario = message.text
        langChainTools = LangChainTools()
        llm = langChainTools.load_llm_openai()

        events = graph.stream(
            {"messages": [("user", pregunta_usuario)],
             "is_last_step": False},
            config, stream_mode="updates"
        )

        for event in events:
            if "agent" in event:
                respuesta_agente = event["agent"]["messages"][-1].content

                # Verificar si la respuesta no está vacía
                if respuesta_agente:
                    bot.send_message(
                        message.chat.id, respuesta_agente,
                        parse_mode="Markdown"
                    )

                    path_voice: str = tts_api(respuesta_agente)
                    with open(path_voice, 'rb') as voice:
                        bot.send_voice(message.chat.id, voice=voice)

                    history.append(HumanMessage(content=pregunta_usuario))
                    history.append(AIMessage(content=respuesta_agente))


# Iniciar el bot
bot.infinity_polling()
