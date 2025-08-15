# backend/controllers/auth_controller.py

from backend.services import auth_service
from backend.schemas.auth_schemas import LoginSchema
from backend.utils.custom_exceptions import ValidationError, UnauthorizedError
from pydantic import ValidationError as PydanticValidationError
from backend.schemas.auth_schemas import RegisterSchema 
from backend.schemas.auth_schemas import RegisterRequestSchema 

def handle_login(request_data):
    """
    Handles the login logic by validating data and calling the service layer.
    This is the function that the API route will call.
    """
    try:
        # Validate incoming JSON against the Pydantic schema
        validated_data = LoginSchema.model_validate(request_data)
        
        # Call the service layer to perform login logic and get the result
        result = auth_service.realizar_login(
            validated_data.email, 
            validated_data.senha
        )
        
        # Return a dictionary and a status code for the response
        return {"success": True, **result}, 200
        
    except PydanticValidationError as e:
        # Handle Pydantic's validation errors by raising our custom exception
        raise ValidationError(details=e.errors())

def handle_register(request_data, current_user):
    """
    Lida com o pedido de registo de um novo utilizador.
    """
    try:
        validated_data = RegisterSchema.model_validate(request_data)
        
        # O ID do admin que está a fazer o pedido vem do token
        admin_id = current_user['usuarioId']
        
        result = auth_service.registrar_novo_usuario(validated_data, admin_id)
        return {"success": True, **result}, 201 # 201 Created
    except PydanticValidationError as e:
        raise ValidationError(details=e.errors())
    
def handle_register_request(request_data):
    try:
        validated_data = RegisterRequestSchema.model_validate(request_data)
        result = auth_service.processar_pedido_registo(validated_data.model_dump())
        return {"success": True, **result}, 200
    except PydanticValidationError as e:
        raise ValidationError(details=e.errors())
    
def handle_get_users(current_user):
    """Lida com o pedido para obter todos os utilizadores."""
    # A verificação de 'admin' é feita no middleware, mas podemos adicionar uma dupla verificação aqui
    if current_user.get('role') != 'admin':
        raise UnauthorizedError(message="Acesso negado. Apenas administradores.")
    
    users = auth_service.get_all_users()
    return {"success": True, "data": users}, 200
