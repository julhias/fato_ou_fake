# backend/api/upload_routes.py

from flask import Blueprint, request, jsonify
from backend.controllers import upload_controller
from backend.middlewares.auth_middleware import token_required

# Define the blueprint for upload-related routes
upload_bp = Blueprint('upload_bp', __name__)

@upload_bp.route('/upload/resultados', methods=['POST'])
@token_required  # Apply the security decorator
def upload_resultados_route(current_user):
    """
    Protected API endpoint for uploading a batch of analysis results.
    """
    # Call the correct handler function from the controller
    response, status_code = upload_controller.handle_upload_resultados(
        request.get_json(),
        current_user['usuarioId'] # Pass the real user ID from the token
    )
    return jsonify(response), status_code

@upload_bp.route('/upload/armazenar', methods=['POST'])
@token_required # Apply the security decorator
def upload_armazenar_route(current_user):
    """
    Protected API endpoint for storing a batch of media.
    """
    # Call the correct handler function from the controller
    response, status_code = upload_controller.handle_armazenar_midia(
        request.get_json(),
        current_user['usuarioId'] # Pass the real user ID from the token
    )
    return jsonify(response), status_code
