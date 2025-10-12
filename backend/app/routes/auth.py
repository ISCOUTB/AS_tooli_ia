from flask import Blueprint, request, jsonify

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Dummy authentication
    if username == 'admin' and password == 'password':
        return jsonify({
            'success': True,
            'data': {'user_id': 123},
            'message': 'Login successful'
        }), 200
    else:
        return jsonify({
            'success': False,
            'data': {},
            'message': 'Invalid credentials'
        }), 401

@auth_bp.route('/profile', methods=['GET'])
def profile():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username == 'admin' and password == 'password':
        return jsonify({
            'success': True,
            'data': {'user_id': 123},
            'message': 'Profile retrieved'
        }), 200
    else:
        return jsonify({
            'success': False,
            'data': {},
            'message': 'Invalid credentials'
        }), 401