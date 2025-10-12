import requests
from app.config import Config

class N8nProxyService:
    def forward_request(self, url: str, user_id: int, payload: dict) -> dict:
        full_payload = {'userId': user_id, **payload}
        try:
            response = requests.post(url, json=full_payload, timeout=Config.N8N_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise Exception('Request to n8n timed out')
        except requests.exceptions.RequestException as e:
            raise Exception(f'Error forwarding request: {str(e)}')