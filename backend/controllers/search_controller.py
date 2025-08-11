# backend/controllers/search_controller.py

from backend.services import search_service
from backend.schemas.search_schemas import PesquisaAvancadaSchema, PesquisarMidiaSchema
from backend.utils.custom_exceptions import ValidationError
from pydantic import ValidationError as PydanticValidationError

def handle_pesquisa_avancada(request_data):
    """
    Handles the advanced search request for analysis results.
    """
    try:
        validated_data = PesquisaAvancadaSchema.model_validate(request_data)
        results = search_service.realizar_pesquisa_avancada(validated_data)
        return {"success": True, "data": results}, 200
    except PydanticValidationError as e:
        raise ValidationError(details=e.errors())

def handle_pesquisa_midia(request_data):
    """
    Handles the search request for stored media.
    """
    try:
        validated_data = PesquisarMidiaSchema.model_validate(request_data)
        results = search_service.realizar_pesquisa_midia(validated_data)
        return {"success": True, "data": results}, 200
    except PydanticValidationError as e:
        raise ValidationError(details=e.errors())
