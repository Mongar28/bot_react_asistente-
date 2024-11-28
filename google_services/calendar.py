"""
Módulo para interactuar con Google Calendar API.
"""

from datetime import datetime
from typing import List, Optional, Dict
from googleapiclient.discovery import build
from .auth import default_auth, CALENDAR_SCOPES

class GoogleCalendar:
    """Clase para interactuar con Google Calendar API."""
    
    def __init__(self):
        """Inicializa el servicio de Calendar."""
        self.auth = default_auth
        self.service = None
    
    def _get_service(self):
        """Obtiene o inicializa el servicio de Calendar."""
        if not self.service:
            creds = self.auth.get_credentials()
            self.service = build('calendar', 'v3', credentials=creds)
        return self.service
    
    def list_events(self, max_results: int = 50) -> List[Dict]:
        """
        Lista los próximos eventos del calendario.
        
        Args:
            max_results: Número máximo de eventos a retornar
            
        Returns:
            List[Dict]: Lista de eventos formateados
        """
        try:
            service = self._get_service()
            now = datetime.utcnow().isoformat() + 'Z'
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return [self._format_event(event) for event in events]
            
        except Exception as e:
            raise Exception(f"Error al listar eventos: {e}")
    
    def _format_event(self, event: Dict) -> Dict:
        """
        Formatea un evento para una mejor presentación.
        
        Args:
            event: Evento raw de Google Calendar
            
        Returns:
            Dict: Evento formateado
        """
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        
        return {
            'id': event['id'],
            'summary': event.get('summary', 'Sin título'),
            'start': start,
            'end': end,
            'description': event.get('description', ''),
            'location': event.get('location', ''),
            'link': event.get('htmlLink', '')
        }
    
    def create_event(
        self,
        summary: str,
        start_time: str,
        end_time: str,
        description: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict:
        """
        Crea un nuevo evento en el calendario.
        
        Args:
            summary: Título del evento
            start_time: Hora de inicio (formato ISO)
            end_time: Hora de fin (formato ISO)
            description: Descripción del evento
            location: Ubicación del evento
            
        Returns:
            Dict: Evento creado y formateado
        """
        try:
            service = self._get_service()
            
            event = {
                'summary': summary,
                'start': {'dateTime': start_time, 'timeZone': 'UTC'},
                'end': {'dateTime': end_time, 'timeZone': 'UTC'}
            }
            
            if description:
                event['description'] = description
            if location:
                event['location'] = location
            
            created_event = service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            return self._format_event(created_event)
            
        except Exception as e:
            raise Exception(f"Error al crear evento: {e}")
