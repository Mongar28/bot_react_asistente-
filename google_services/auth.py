"""
Módulo centralizado para la autenticación con Google APIs.
"""

import logging
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from typing import List, Optional

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class GoogleAuth:
    """Clase para manejar la autenticación con Google APIs."""
    
    def __init__(self, scopes: List[str], credentials_file: str = 'google_credentials.json'):
        """
        Inicializa el manejador de autenticación.
        
        Args:
            scopes: Lista de scopes requeridos para las APIs
            credentials_file: Ruta al archivo de credenciales
        """
        self.scopes = scopes
        self.credentials_file = credentials_file
        self._credentials = None
    
    def get_credentials(self) -> Optional[Credentials]:
        """
        Obtiene o refresca las credenciales de Google.
        
        Returns:
            Credentials: Objeto de credenciales de Google
        """
        if self._credentials and self._credentials.valid:
            return self._credentials
            
        if os.path.exists('token.json'):
            try:
                self._credentials = Credentials.from_authorized_user_file('token.json', self.scopes)
            except Exception as e:
                logging.error(f"Error al cargar token.json: {e}")
        
        if not self._credentials or not self._credentials.valid:
            if self._credentials and self._credentials.expired and self._credentials.refresh_token:
                try:
                    self._credentials.refresh(Request())
                except Exception as e:
                    logging.error(f"Error al refrescar el token: {e}")
                    self._credentials = None
            
            if not self._credentials:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.scopes
                    )
                    self._credentials = flow.run_local_server(port=0)
                except Exception as e:
                    logging.error(f"Error durante la autenticación: {e}")
                    raise e
            
            try:
                with open('token.json', 'w') as token:
                    token.write(self._credentials.to_json())
            except Exception as e:
                logging.error(f"Error al guardar token.json: {e}")
        
        return self._credentials

# Scopes predefinidos para diferentes servicios
CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar']
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]

# Instancia por defecto con todos los scopes
DEFAULT_SCOPES = CALENDAR_SCOPES + GMAIL_SCOPES
default_auth = GoogleAuth(DEFAULT_SCOPES)
get_credentials = default_auth.get_credentials
