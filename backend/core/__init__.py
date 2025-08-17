# backend/core/__init__.py

from flask import Flask, send_from_directory
from flask_cors import CORS
from backend.api.auth_routes import auth_bp
from backend.api.upload_routes import upload_bp
from backend.api.search_routes import search_bp
from backend.core.error_handler import register_error_handlers
from backend.core.config import settings

def create_app():
    """
    Cria e configura a instância da aplicação Flask (Application Factory).
    """
    app = Flask(__name__)
    CORS(app) # Habilita CORS para todas as rotas

    # Registra os blueprints (conjuntos de rotas)
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(upload_bp, url_prefix='/api')
    app.register_blueprint(search_bp, url_prefix='/api')

    # --- NOVA ROTA PARA SERVIR ARQUIVOS ---
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        """
        Serve os arquivos que foram enviados e estão na pasta UPLOAD_FOLDER.
        A URL será, por exemplo, http://127.0.0.1:5000/uploads/meu_arquivo.jpg
        """
        return send_from_directory(settings.UPLOAD_FOLDER, filename)

    # Registra os manipuladores de erro personalizados
    register_error_handlers(app)
    
    return app