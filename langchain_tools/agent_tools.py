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
from google_services.gmail import Gmail
from google_services.calendar import GoogleCalendar


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


@tool
def gmail_send_email(to: str, subject: str, body: str) -> dict:
    """
    Use this tool to send an email using Gmail.
    
    Args:
        to: Email address of the recipient
        subject: Subject of the email
        body: Content of the email
        
    Returns:
        dict: Response from the Gmail service
    """
    gmail = Gmail()
    return gmail.send_email(to=to, subject=subject, body=body)


@tool
def gmail_list_messages(max_results: int = 5) -> list:
    """
    Use this tool to list recent messages from Gmail inbox.
    
    Args:
        max_results: Maximum number of messages to return (default: 5)
        
    Returns:
        list: List of recent messages
    """
    gmail = Gmail()
    return gmail.list_messages(max_results=max_results)


@tool
def calendar_list_events(max_results: int = 10) -> list:
    """
    Use this tool to list upcoming calendar events.
    
    Args:
        max_results: Maximum number of events to return (default: 10)
        
    Returns:
        list: List of upcoming events
    """
    calendar = GoogleCalendar()
    return calendar.list_events(max_results=max_results)


@tool
def calendar_create_event(summary: str, start_time: str, end_time: str, description: str = None, location: str = None) -> dict:
    """
    Use this tool to create a new calendar event.
    
    Args:
        summary: Title of the event
        start_time: Start time in ISO format
        end_time: End time in ISO format
        description: Optional description of the event
        location: Optional location of the event
        
    Returns:
        dict: Created event details
    """
    calendar = GoogleCalendar()
    return calendar.create_event(
        summary=summary,
        start_time=start_time,
        end_time=end_time,
        description=description,
        location=location
    )
