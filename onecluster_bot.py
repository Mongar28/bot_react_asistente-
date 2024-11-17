import telebot
from dotenv import load_dotenv
import os
from api_openai.whisper import whisper_api, tts_api
from langchain_tools.agent_tools import LangChainTools
from langchain_tools.agents import AgentTools
from langchain_core.messages import AIMessage, HumanMessage
# from tools.scaped import scaped

# Configuración del bot
load_dotenv()
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

        agentTools = AgentTools()
        tools = agentTools.load_tools()
        agent_executor = agentTools.load_agent(llm, tools)

        respuesta_agente = agent_executor.invoke(
            {
                "input": pregunta_usuario,
                "chat_history": history,
            }
        )

        bot.send_message(message.chat.id, respuesta_agente["output"],
                         parse_mode="Markdown")

        path_voice: str = tts_api(respuesta_agente["output"])
        with open(path_voice, 'rb') as voice:
            bot.send_voice(message.chat.id, voice=voice)

        history.append(HumanMessage(content=pregunta_usuario))
        history.append(AIMessage(content=respuesta_agente["output"]))

    # Si el mensaje es de texto
    if message.text:
        pregunta_usuario = message.text
        langChainTools = LangChainTools()
        llm = langChainTools.load_llm_openai()

        agentTools = AgentTools()
        tools = agentTools.load_tools()
        agent_executor = agentTools.load_agent(llm, tools)

        respuesta_agente = agent_executor.invoke(
            {
                "input": pregunta_usuario,
                "chat_history": history,
            }
        )

        # texto_respuesta: str = scaped(respuesta_agente["output"])
        texto_respuesta: str = respuesta_agente["output"]
        bot.send_message(
            message.chat.id, texto_respuesta,
            parse_mode="Markdown")

        # Mandar mensaje de voz
        # path_voice: str = tts_api(respuesta_agente["output"])
        # with open(path_voice, 'rb') as voice:
        #     bot.send_voice(message.chat.id, voice=voice)

        history.append(HumanMessage(content=pregunta_usuario))
        history.append(AIMessage(content=respuesta_agente["output"]))
        # print(history)

    # Enviar el historial después de cada interacción
    # bot.send_message(message.chat.id, history)


# while True:
#     time.sleep(60)
#     mensaje = 'Que mas pues!!'
#     bot.send_message('5076346205', mensaje)

bot.infinity_polling()
