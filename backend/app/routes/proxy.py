from flask import Blueprint, request, jsonify, abort
from app.services.n8n_proxy import N8nProxyService
from app.config import Config

proxy_bp = Blueprint('proxy', __name__)
n8n_service = N8nProxyService()

def validate_credentials():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if username == 'admin' and password == 'password':
        return 123  # user_id
    else:
        abort(401, description='Invalid credentials')

@proxy_bp.route('/chat/message', methods=['POST'])
def chat_message():
    user_id = validate_credentials()
    payload = request.get_json() or {}
    # Remove credentials from payload before forwarding
    payload.pop('username', None)
    payload.pop('password', None)

    try:
        result = n8n_service.forward_request(Config.N8N_WEBHOOK_URL_CHAT, user_id, payload)
        # result: {'status_code': int, 'ok': bool, 'body': ...}
        if not result.get('ok'):
            return jsonify({
                'success': False,
                'data': result.get('body', {}),
                'message': f'n8n returned status {result.get("status_code")}'
            }), 502

        # Normalize body into { 'message': '...' } shape expected by frontend
        body = result.get('body', {})
        if isinstance(body, dict) and 'message' in body:
            response_body = body
        elif isinstance(body, dict) and 'text' in body:
            response_body = {'message': body.get('text')}
        elif isinstance(body, str):
            response_body = {'message': body}
        else:
            response_body = {'message': str(body)}

        return jsonify({
            'success': True,
            'data': response_body,
            'message': 'Message forwarded'
        }), 200

    except RuntimeError as e:
        return jsonify({
            'success': False,
            'data': {},
            'message': str(e)
        }), 504
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {},
            'message': f'Unexpected error: {e}'
        }), 500

@proxy_bp.route('/tickets', methods=['GET'])
def get_tickets():
    user_id = validate_credentials()
    payload = {}
    try:
        response = n8n_service.forward_request(Config.N8N_WEBHOOK_URL_GLPI, user_id, payload)
        return jsonify({
            'success': True,
            'data': response,
            'message': 'Tickets retrieved'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {},
            'message': str(e)
        }), 500

@proxy_bp.route('/tickets', methods=['POST'])
def create_ticket():
    user_id = validate_credentials()
    payload = request.get_json() or {}
    # Remove credentials from payload before forwarding
    payload.pop('username', None)
    payload.pop('password', None)
    try:
        response = n8n_service.forward_request(Config.N8N_WEBHOOK_URL_GLPI, user_id, payload)
        return jsonify({
            'success': True,
            'data': response,
            'message': 'Ticket created'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {},
            'message': str(e)
        }), 500

@proxy_bp.route('/inventory', methods=['GET'])
def get_inventory():
    user_id = validate_credentials()
    payload = {}
    try:
        response = n8n_service.forward_request(Config.N8N_WEBHOOK_URL_GLPI, user_id, payload)
        return jsonify({
            'success': True,
            'data': response,
            'message': 'Inventory retrieved'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {},
            'message': str(e)
        }), 500