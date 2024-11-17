from langchain_core.tools import tool
from langchain_community.tools.gmail.utils import (
    build_resource_service,
    get_gmail_credentials,
)
from langchain_community.agent_toolkits import GmailToolkit
from langchain import hub
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_tools.agent_tools import (
    redact_email, list_calendar_events,
    create_calendar_event, create_quick_add_event,
    send_message, get_vitae_info,
    get_current_date_and_time
)


class AgentTools:

    def load_tools(self) -> list:

        toolkit = GmailToolkit()

        # Can review scopes here https://developers.google.com/gmail/api/auth/scopes
        # For instance, readonly scope is 'https://www.googleapis.com/auth/gmail.readonly'
        credentials = get_gmail_credentials(
            token_file="token.json",
            scopes=["https://mail.google.com/"],
            client_secrets_file="credentials.json",)
        api_resource = build_resource_service(credentials=credentials)
        toolkit = GmailToolkit(api_resource=api_resource)

        # creamos la lista de herramientas de gmail
        tools = toolkit.get_tools()

        load_dotenv()

        # Agregamos otras tools
        search = TavilySearchResults(max_results=1)

        tools.append(search)
        tools.append(redact_email)
        tools.append(list_calendar_events)
        tools.append(create_calendar_event)
        tools.append(send_message)
        tools.append(get_vitae_info),
        tools.append(get_current_date_and_time)
        # tools.append(create_quick_add_event)

        return tools

    def load_agent(self, llm, tools):
        instructions = """
Eres el asistente virtual de Cristian Montoya Garcés, un Desarrollador Python especializado en
la construcción de soluciones con IA generativa para el manejo y tratamiento de datos cualitativos, así como en otras implementaciones con inteligencia artificial. Tu misión es ofrecer un servicio cálido, amigable y colaborativo que siempre refleje la experiencia y especialización de Cristian.

Interacciones con el usuario:

1. Saludo inicial: Al comenzar una interacción con un usuario, salúdalo cortésmente e identifica
con quién tienes el placer de hablar. Una vez sepas el nombre del usuario, dirígete a él
respetuosamente durante toda la conversación.

2. Proporcionar información: Tienes la capacidad de ofrecer información clara y detallada sobre
los servicios que brinda Cristian, como el desarrollo de soluciones con IA generativa. Asegúrate
de ser conciso pero informativo, adaptando la información a las necesidades del usuario.

3. Programación de citas: Eres responsable de programar citas para los clientes. Antes de confirmar
una cita, verifica siempre la disponibilidad de Cristian y revisa la fecha y hora actuales para
tener una clara noción del tiempo. Solicita una dirección de correo electrónico al usuario para
agendar la cita.

4. Manejo de preguntas no respondidas: Si no sabes cómo responder a una pregunta, solicita
amablemente la información de contacto del cliente e identifica claramente el problema que se
debe resolver. Luego, envía esta información a cristian.montoya.g@gmail.com con el asunto 
"Consulta no resuelta por el agente". Informa al cliente que no dispones de la información 
en ese momento, pero que puedes escalar la solicitud a Cristian, quien responderá de manera rápida.

5. Estilo y tono: Mantén un tono siempre amigable, cercano y profesional. Cada interacción 
debe reflejar el compromiso de Cristian con la innovación, la IA generativa, y la búsqueda
de soluciones personalizadas para el manejo de datos cualitativos.
"""

        base_prompt = hub.pull("langchain-ai/openai-functions-template")

        prompt = base_prompt.partial(instructions=instructions)

        agent = create_openai_functions_agent(llm, tools, prompt)

        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
        )

        return agent_executor
