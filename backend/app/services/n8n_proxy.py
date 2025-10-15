import logging
import requests
from app.config import Config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class N8nProxyService:
    def forward_request(self, url: str, user_id: int, payload: dict) -> dict:
        """Forward only the message to n8n and return structured result for proxy.

        Returns a dict with keys: status_code, ok, body (JSON or text).
        Raises RuntimeError on request-level errors with descriptive message.
        """
        message = ''
        if isinstance(payload, dict):
            message = payload.get('message', '')
        full_payload = {'message': message}
        logger.info('Forwarding to n8n %s payload=%s', url, full_payload)

        try:
            resp = requests.post(url, json=full_payload, timeout=Config.N8N_TIMEOUT)
            status = resp.status_code
            text = resp.text
            try:
                body = resp.json()
            except ValueError:
                body = {'text': text}

            logger.info('n8n responded status=%s body=%s', status, body)

            if not resp.ok:
                # Return structured error information
                return {'status_code': status, 'ok': False, 'body': body}

            return {'status_code': status, 'ok': True, 'body': body}

        except requests.exceptions.Timeout as e:
            logger.exception('Timeout when calling n8n')
            raise RuntimeError(f'Timeout after {Config.N8N_TIMEOUT}s when calling n8n') from e
        except requests.exceptions.RequestException as e:
            logger.exception('RequestException when calling n8n')
            raise RuntimeError(f'Connection error when calling n8n: {e}') from e