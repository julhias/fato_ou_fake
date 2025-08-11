# backend/core/__init__.py

from flask import Flask
from flask_cors import CORS

# 1. Import the settings object that loads your .env file
from backend.core.config import settings

# Import your blueprints
from backend.api.auth_routes import auth_bp
from backend.api.upload_routes import upload_bp
from backend.api.search_routes import search_bp 
from backend.core.error_handler import register_error_handlers

def create_app():
    app = Flask(__name__)
    CORS(app)

    # 2. This is the crucial step!
    # Load the SECRET_KEY from your settings into the Flask app's config.
    # Now, current_app.config.get('SECRET_KEY') will return the correct value.
    app.config['SECRET_KEY'] = settings.SECRET_KEY

    # Optional: Add this line to debug and confirm the key is loaded on startup
    print(f"DEBUG: SECRET_KEY loaded into app.config: {app.config['SECRET_KEY']}")

    # Register all blueprints with the app
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(upload_bp, url_prefix='/api')
    app.register_blueprint(search_bp, url_prefix='/api')

    # Register the global error handlers
    register_error_handlers(app)

    return app