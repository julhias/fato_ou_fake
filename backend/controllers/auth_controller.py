# backend/controllers/auth_controller.py

from backend.services import auth_service
from backend.schemas.auth_schemas import LoginSchema
from backend.utils.custom_exceptions import ValidationError
from pydantic import ValidationError as PydanticValidationError

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

