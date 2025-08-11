# backend/core/error_handler.py
from flask import jsonify
from backend.utils.custom_exceptions import ServiceError, ValidationError
from pydantic import ValidationError as PydanticValidationError

def register_error_handlers(app):
    @app.errorhandler(ServiceError)
    def handle_service_error(error):
        response = {"success": False, "error": error.message}
        return jsonify(response), error.status_code

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        response = {"success": False, "error": error.message, "details": error.details}
        return jsonify(response), error.status_code
        
    @app.errorhandler(PydanticValidationError)
    def handle_pydantic_validation_error(error):
        # Captura erros de validação do Pydantic
        response = {"success": False, "error": "Dados de entrada inválidos", "details": error.errors()}
        return jsonify(response), 400

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        print(f"Erro inesperado: {error}") # Logar o erro é crucial
        response = {"success": False, "error": "Ocorreu um erro interno no servidor."}
        return jsonify(response), 500