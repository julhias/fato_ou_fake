# backend/middlewares/auth_middleware.py

from functools import wraps
from flask import request, jsonify, current_app 
import jwt
from datetime import timedelta

def token_required(f):
    """
    Um decorador para garantir que um JWT válido esteja presente no cabeçalho da requisição.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"success": False, "message": "Token Bearer mal formatado"}), 401

        if not token:
            return jsonify({"success": False, "message": "Token está faltando!"}), 401

        try:
            key_para_validar = current_app.config.get('SECRET_KEY')
            
            # --- DEBUG ADICIONADO ---
            # Imprime a chave que está sendo usada para VALIDAR o token.
            # Compare este output com a chave usada para GERAR o token.
            print(f"DEBUG: Chave usada para VALIDAR o token: '{key_para_validar}'")
            # --------------------------
            
            # --- CORREÇÃO FINAL: Adiciona um 'leeway' de 10 segundos ---
            # Isso corrige problemas de desvio de relógio (clock skew) entre a
            # criação e a validação do token.
            data = jwt.decode(
                token, 
                key_para_validar, 
                leeway=timedelta(seconds=10), 
                algorithms=["HS256"]
            )
            current_user = {'usuarioId': data['sub']}

        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token expirou!"}), 401
        except jwt.InvalidTokenError:
            # Se o erro persistir mesmo com o leeway, o problema é outro.
            return jsonify({"success": False, "message": "Token é inválido!"}), 401
        except Exception as e:
            return jsonify({"success": False, "message": f"Ocorreu um erro inesperado: {str(e)}"}), 500

        return f(current_user, *args, **kwargs)

    return decorated