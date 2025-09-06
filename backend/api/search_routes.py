# backend/api/search_routes.py

from flask import Blueprint, request, jsonify
from backend.controllers import search_controller
# A linha abaixo não é mais estritamente necessária se token_required não for usado aqui.
# from backend.middlewares.auth_middleware import token_required

search_bp = Blueprint('search_bp', __name__)

# --- Rota de Pesquisa de Resultados ---
@search_bp.route('/search/resultados', methods=['POST'])
def pesquisa_avancada_route():
    """
    Endpoint público para pesquisa avançada nos resultados da análise.
    """
    response, status_code = search_controller.handle_pesquisa_avancada(request.get_json())
    return jsonify(response), status_code

# --- Rota de Pesquisa de Mídia ---
@search_bp.route('/search/midia', methods=['POST'])
def pesquisar_midia_route():
    """
    Endpoint público para pesquisa de mídia armazenada.
    """
    response, status_code = search_controller.handle_pesquisa_midia(request.get_json())
    return jsonify(response), status_code