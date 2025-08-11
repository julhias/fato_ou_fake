# backend/controllers/upload_controller.py

from backend.services import upload_service
from backend.schemas.upload_schemas import UploadResultadosSchema, ArmazenarMidiaSchema
from backend.utils.custom_exceptions import ValidationError
from pydantic import ValidationError as PydanticValidationError

def handle_upload_resultados(request_data, usuario_id):
    """
    Lida com a lógica de negócio para o upload de um lote de resultados de análise.
    Valida os dados e chama a camada de serviço.
    """
    try:
        validated_data = UploadResultadosSchema.model_validate(request_data)
        # Passa o ID real do utilizador (do token) para a camada de serviço
        result = upload_service.criar_lote_resultados(validated_data, usuario_id)
        return {"success": True, **result}, 200
    except PydanticValidationError as e:
        raise ValidationError(details=e.errors())

def handle_armazenar_midia(request_data, usuario_id):
    """
    Lida com a lógica de negócio para armazenar um lote de mídias.
    Valida os dados e chama a camada de serviço.
    """
    try:
        validated_data = ArmazenarMidiaSchema.model_validate(request_data)
        # Passa o ID real do utilizador (do token) para a camada de serviço
        result = upload_service.salvar_midia(validated_data, usuario_id)
        return {"success": True, **result}, 200
    except PydanticValidationError as e:
        raise ValidationError(details=e.errors())
