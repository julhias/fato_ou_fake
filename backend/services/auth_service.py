# backend/services/auth_service.py

from flask import current_app
from backend.repository import db_repository
from backend.utils.custom_exceptions import UnauthorizedError
import jwt
from datetime import datetime, timedelta, timezone
from backend.schemas.auth_schemas import RegisterSchema 
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.core.config import settings

def realizar_login(email, senha):
    """
    Valida as credenciais do usuário e retorna um JWT e a role em caso de sucesso.
    """
    usuario_id = db_repository.validar_login_repo(email, senha)
    
    if not usuario_id or usuario_id == 0:
        raise UnauthorizedError("Email ou senha inválidos")


    # Após validar o login, buscamos os detalhes do usuário, incluindo a role.
    user_details = db_repository.get_user_by_id_repo(usuario_id)
    if not user_details:
        # Isso é uma segurança, caso o ID seja válido mas o usuário não seja encontrado
        raise UnauthorizedError("Usuário não encontrado após validação.")
    # ------------------------------------

    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=1),
        'iat': datetime.now(timezone.utc),
        'sub': str(usuario_id)
    }
    
    secret_key = current_app.config.get('SECRET_KEY')
    
    token = jwt.encode(
        payload,
        secret_key,
        algorithm='HS256'
    )

    # incluímos a 'role' na resposta para o frontend.
    return {
        "usuarioId": usuario_id,
        "token": token,
        "role": user_details['Role'] 
    }

def registrar_novo_usuario(data: RegisterSchema, admin_id: int):
    """
    Prepara os argumentos e chama o repositório para registar um novo utilizador.
    """
    args = (
        admin_id,
        data.nome,
        data.email,
        data.senha,
        data.role
    )
    db_repository.registrar_usuario_repo(args)
    return {"message": f"Utilizador '{data.nome}' registado com sucesso."}

def processar_pedido_registo(data):
    """
    Busca os emails dos administradores e envia uma notificação de pedido de registo.
    """
    admin_emails = db_repository.get_admin_emails_repo()
    
    if not admin_emails:
        # Se não houver administradores, não há para quem enviar o email.
        raise ValueError("Nenhum administrador encontrado para notificar.")

    # Configurações do email
    sender_email = settings.MAIL_USERNAME
    password = settings.MAIL_PASSWORD
    
    # Cria a mensagem do email
    message = MIMEMultipart("alternative")
    message["Subject"] = "Novo Pedido de Registo na Plataforma Fato ou Fake"
    message["From"] = sender_email
    message["To"] = ", ".join(admin_emails) # Envia para todos os admins

    text = f"""
    Olá Administrador,

    Um novo utilizador solicitou o registo na plataforma.
    
    Nome: {data['nome']}
    Email: {data['email']}
    
    Por favor, aceda ao sistema para criar a conta deste utilizador, se for apropriado.
    
    Atenciosamente,
    Sistema Fato ou Fake
    """
    
    part = MIMEText(text, "plain")
    message.attach(part)

    # Envia o email
    try:
        context = smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT)
        context.starttls()
        context.login(sender_email, password)
        context.sendmail(sender_email, admin_emails, message.as_string())
    except Exception as e:
        # Se o envio de email falhar, lança um erro
        raise ConnectionError(f"Falha ao enviar o email de notificação: {e}")
    finally:
        context.quit()

    return {"message": "O seu pedido de registo foi enviado com sucesso. Um administrador irá analisá-lo."}

def get_all_users():
    """Serviço para obter todos os utilizadores."""
    return db_repository.get_all_users_repo()
