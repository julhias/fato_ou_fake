# backend/services/auth_service.py

from flask import current_app
from backend.repository import db_repository
from backend.utils.custom_exceptions import UnauthorizedError
import jwt
from datetime import datetime, timedelta, timezone

def realizar_login(email, senha):
    """
    Valida as credenciais do usuário e retorna um JWT em caso de sucesso.
    """
    usuario_id = db_repository.validar_login_repo(email, senha)
    
    if not usuario_id or usuario_id == 0:
        raise UnauthorizedError("Email ou senha inválidos")

    # --- CORREÇÃO DEFINITIVA ---
    # O campo 'sub' (subject) do JWT DEVE ser uma string, conforme a especificação.
    # Convertemos o ID do usuário para string antes de criar o payload.
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=1),
        'iat': datetime.now(timezone.utc),
        'sub': str(usuario_id) # <-- AQUI ESTÁ A CORREÇÃO!
    }
    
    secret_key = current_app.config.get('SECRET_KEY')
    
    token = jwt.encode(
        payload,
        secret_key,
        algorithm='HS256'
    )

    # O teste de sanidade não é mais necessário, mas pode ser mantido se desejar.
    try:
        jwt.decode(token, secret_key, algorithms=["HS256"])
        print("DEBUG: SUCESSO! O token foi criado e validado internamente.")
    except jwt.InvalidTokenError as e:
        print(f"DEBUG: FALHA! Algo ainda está errado. Erro: {e}")

    return {"usuarioId": usuario_id, "token": token}