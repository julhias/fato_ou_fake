# backend/core/__init__.py

from flask import Flask, send_from_directory
from flask_cors import CORS
import os

# 1. Importar as configurações (que agora contêm UPLOAD_FOLDER)
from backend.core.config import settings

# Importar blueprints
from backend.api.auth_routes import auth_bp
from backend.api.upload_routes import upload_bp
from backend.api.search_routes import search_bp
from backend.core.error_handler import register_error_handlers

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configurar a chave secreta e a pasta de upload no app Flask
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.config['UPLOAD_FOLDER'] = settings.UPLOAD_FOLDER

    # Registrar blueprints da API
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(upload_bp, url_prefix='/api')
    app.register_blueprint(search_bp, url_prefix='/api')

    # Registrar manipuladores de erro globais
    register_error_handlers(app)

    @app.route('/uploads/<path:filename>')
    def serve_uploaded_file(filename):
        """
        Serve arquivos estáticos da pasta de upload configurada.
        Isto permite que as URLs /uploads/nome_do_arquivo.jpg funcionem publicamente.
        Usar send_from_directory é a forma segura de fazer isso.
        """
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    # --- FIM DA MODIFICAÇÃO ---

    return app