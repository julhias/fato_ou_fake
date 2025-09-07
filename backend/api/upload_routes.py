# backend/api/upload_routes.py

from flask import Blueprint, request, jsonify
from backend.controllers import upload_controller
from backend.middlewares.auth_middleware import token_required

upload_bp = Blueprint('upload_bp', __name__)

@upload_bp.route('/upload/resultados', methods=['POST'])
@token_required
def upload_resultados_route(current_user):
    """
    Endpoint para fazer o upload de um lote de resultados de análise (via JSON).
    """
    response, status_code = upload_controller.handle_upload_resultados(
        request.get_json(),
        current_user['usuarioId']
    )
    return jsonify(response), status_code

@upload_bp.route('/upload/armazenar', methods=['POST'])
@token_required
def upload_armazenar_route(current_user):
    """
    Endpoint para armazenar mídias.
    Aceita dados de formulário (multipart/form-data) que podem incluir arquivos.
    """
    # Passa os dados do formulário e os arquivos para o controlador
    response, status_code = upload_controller.handle_armazenar_midia(
        request.form,
        request.files,
        current_user['usuarioId']
    )
    return jsonify(response), status_code
