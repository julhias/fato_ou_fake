# backend/controllers/upload_controller.py

from backend.services import upload_service
from backend.schemas.upload_schemas import UploadResultadosSchema, ArmazenarMidiaSchema
from backend.utils.custom_exceptions import ValidationError
from pydantic import ValidationError as PydanticValidationError
import json

def handle_upload_resultados(request_data, usuario_id):
    """Lida com o upload de um ficheiro JSON/CSV de resultados."""
    try:
        validated_data = UploadResultadosSchema.model_validate(request_data)
        result = upload_service.criar_lote_resultados(validated_data, usuario_id)
        return {"success": True, **result}, 200
    except (PydanticValidationError, ValueError) as e:
        raise ValidationError(details=str(e))

def handle_armazenar_midia(form_data, files, usuario_id):
    """
    Lida com o upload de ficheiros de mídia. Extrai os dados do formulário
    e os ficheiros para serem processados pelo serviço.
    """
    try:
        # Pydantic pode validar um dicionário, então convertemos o form para um
        form_data_dict = form_data.to_dict()

        # O campo 'tiposConteudo' vem como uma string JSON do formulário,
        # então precisamos convertê-lo para uma lista Python antes de validar.
        if 'tiposConteudo' in form_data_dict:
            form_data_dict['tiposConteudo'] = json.loads(form_data_dict['tiposConteudo'])
            
        validated_data = ArmazenarMidiaSchema.model_validate(form_data_dict)
        
        # Passa os dados validados e os arquivos para o serviço
        result = upload_service.salvar_midia(validated_data, files, usuario_id)
        return {"success": True, **result}, 200
    except (PydanticValidationError, ValueError, json.JSONDecodeError) as e:
        # Captura erros de validação, de lógica ou de JSON inválido
        raise ValidationError(details=str(e))