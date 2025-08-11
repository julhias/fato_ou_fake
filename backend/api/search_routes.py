# backend/api/search_routes.py

from flask import Blueprint, request, jsonify
from backend.controllers import search_controller
from backend.middlewares.auth_middleware import token_required

search_bp = Blueprint('search_bp', __name__)

@search_bp.route('/search/resultados', methods=['POST'])
@token_required
def pesquisa_avancada_route(current_user):
    """
    Protected API endpoint for advanced search on analysis results.
    """
    response, status_code = search_controller.handle_pesquisa_avancada(request.get_json())
    return jsonify(response), status_code

@search_bp.route('/search/midia', methods=['POST'])
@token_required
def pesquisar_midia_route(current_user):
    """
    Protected API endpoint for searching stored media.
    """
    response, status_code = search_controller.handle_pesquisa_midia(request.get_json())
    return jsonify(response), status_code
