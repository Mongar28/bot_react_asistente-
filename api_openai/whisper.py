from dotenv import load_dotenv
import os
from openai import OpenAI


def whisper_api(file_path: str) -> str:
    # cargar la variable del entorno desde el archivo .env
    load_dotenv()

    # Usar la variable de entorno API_KEY
    api_key: str = os.getenv("OPENAI_API_KEY")

    # Cargar el modelo whisper
    client = OpenAI(api_key=api_key)

    audio_file = open(file_path, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text"
    )

    return transcription


def tts_api(text: str):
    # cargar la variable del entorno desde el archivo .env
    load_dotenv()

    # Usar la variable de entorno API_KEY
    api_key: str = os.getenv("OPENAI_API_KEY")

    # Cargar el modelo whisper
    client = OpenAI(api_key=api_key)

    speech_file_path = os.path.join('audios', 'voice.ogg')
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )

    response.stream_to_file(speech_file_path)

    return speech_file_path
