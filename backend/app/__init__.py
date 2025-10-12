from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret')

    CORS(app)

    from app.routes.auth import auth_bp
    from app.routes.proxy import proxy_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(proxy_bp, url_prefix='/api')

    return app