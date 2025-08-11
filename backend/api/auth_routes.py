# backend/api/auth_routes.py

from flask import Blueprint, request, jsonify
from backend.controllers import auth_controller

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