"""
Módulo para interactuar con Gmail API.
"""

from typing import Optional, Dict, List
from googleapiclient.discovery import build
from .auth import GoogleAuth, GMAIL_SCOPES
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Gmail:
    """Clase para manejar operaciones con Gmail."""
    
    def __init__(self):
        """Inicializa el servicio de Gmail."""
        self.auth = GoogleAuth(GMAIL_SCOPES)
        self.service = None
    
    def _get_service(self):
        """Obtiene o inicializa el servicio de Gmail."""
        if not self.service:
            creds = self.auth.get_credentials()
            self.service = build('gmail', 'v1', credentials=creds)
        return self.service
    
    def get_profile(self) -> Dict:
        """
        Obtiene el perfil del usuario.
        
        Returns:
            Dict: Información del perfil
        """
        try:
            service = self._get_service()
            profile = service.users().getProfile(userId='me').execute()
            return profile
            
        except Exception as e:
            raise Exception(f"Error al obtener perfil: {e}")
    
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        html: bool = False
    ) -> Dict:
        """
        Envía un email.
        
        Args:
            to: Destinatario
            subject: Asunto
            body: Cuerpo del mensaje
            cc: Lista de destinatarios en copia
            bcc: Lista de destinatarios en copia oculta
            html: Si el cuerpo es HTML
            
        Returns:
            Dict: Respuesta del servicio
        """
        try:
            service = self._get_service()
            
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            
            if cc:
                message['cc'] = ','.join(cc)
            if bcc:
                message['bcc'] = ','.join(bcc)
            
            # Crear el cuerpo del mensaje
            msg = MIMEText(body, 'html' if html else 'plain')
            message.attach(msg)
            
            # Codificar el mensaje
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Enviar el mensaje
            sent_message = service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            
            return sent_message
            
        except Exception as e:
            raise Exception(f"Error al enviar email: {e}")
    
    def list_messages(self, max_results: int = 10) -> List[Dict]:
        """
        Lista los últimos mensajes recibidos.
        
        Args:
            max_results: Número máximo de mensajes a retornar
            
        Returns:
            List[Dict]: Lista de mensajes formateados
        """
        try:
            service = self._get_service()
            
            messages = service.users().messages().list(
                userId='me',
                maxResults=max_results,
                labelIds=['INBOX']
            ).execute()
            
            results = []
            for msg in messages.get('messages', []):
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id']
                ).execute()
                
                headers = message['payload']['headers']
                subject = next(
                    (h['value'] for h in headers if h['name'].lower() == 'subject'),
                    'Sin asunto'
                )
                from_email = next(
                    (h['value'] for h in headers if h['name'].lower() == 'from'),
                    'Desconocido'
                )
                
                results.append({
                    'id': message['id'],
                    'subject': subject,
                    'from': from_email,
                    'snippet': message.get('snippet', ''),
                    'date': next(
                        (h['value'] for h in headers if h['name'].lower() == 'date'),
                        ''
                    )
                })
            
            return results
            
        except Exception as e:
            raise Exception(f"Error al listar mensajes: {e}")
