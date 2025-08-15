# backend/api/auth_routes.py

from flask import Blueprint, request, jsonify
from backend.controllers import auth_controller
from backend.middlewares.auth_middleware import token_required # Certifique-se de que tem este import

# Define the blueprint for authentication routes
auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['POST'])
def login_route():
    """
    API route for user login. It receives the web request and passes the data
    to the controller layer to handle the logic.
    """
    # Call the controller function to handle the business logic
    response, status_code = auth_controller.handle_login(request.get_json())
    
    # Take the controller's response and format it as a JSON response for the client
    return jsonify(response), status_code

@auth_bp.route('/register', methods=['POST'])
@token_required # Protege o endpoint, apenas utilizadores logados podem aceder
def register_route(current_user):
    """
    Endpoint da API para um admin registar um novo utilizador.
    """
    response, status_code = auth_controller.handle_register(request.get_json(), current_user)
    return jsonify(response), status_code

@auth_bp.route('/request-registration', methods=['POST'])
def request_registration_route():
    """Endpoint público para solicitar o registo."""
    response, status_code = auth_controller.handle_register_request(request.get_json())
    return jsonify(response), status_code

@auth_bp.route('/users', methods=['GET'])
@token_required
def get_users_route(current_user):
    """Endpoint para obter a lista de todos os utilizadores (apenas para admins)."""
    response, status_code = auth_controller.handle_get_users(current_user)
    return jsonify(response), status_code