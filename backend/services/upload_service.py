# backend/services/upload_service.py

from backend.repository import db_repository
from backend.schemas.upload_schemas import UploadResultadosSchema, ArmazenarMidiaSchema, LoteDadosItem
import json
import requests

def extrair_id_gdrive(url: str) -> str:
    """Extrai o ID do ficheiro de uma URL do Google Drive."""
    try:
        return url.split('/d/')[1].split('/')[0]
    except IndexError:
        return url.split('id=')[1].split('&')[0]

def criar_lote_resultados(data: UploadResultadosSchema, usuario_id: int):
    lote_dados_final = data.loteDados

    if not lote_dados_final and data.gdriveUrl:
        try:
            file_id = extrair_id_gdrive(data.gdriveUrl)
            download_url = f'https://drive.google.com/uc?export=download&id={file_id}'
            response = requests.get(download_url)
            response.raise_for_status()
            
            lote_dados_brutos = response.json()
            lote_dados_final = [LoteDadosItem.model_validate(item) for item in lote_dados_brutos]

        except Exception as e:
            raise ValueError(f"Não foi possível processar o link do Google Drive: {e}")

    if not lote_dados_final:
        raise ValueError("Nenhum dado de lote fornecido (nem via arquivo, nem via Google Drive).")

    for item in lote_dados_final:
        if not item.categoriaDetectada:
            item.categoriaDetectada = "Desconhecida"

    parametros_json = json.dumps(data.parametrosAlgoritmo)
    tipos_conteudo_json = json.dumps(data.tiposConteudo)
    
    # --- CORREÇÃO APLICADA AQUI ---
    # Usamos exclude_none=True para remover quaisquer campos com valor None (como datas opcionais).
    # Isso garante que o JSON_EXTRACT no MySQL retornará um NULL verdadeiro, que é aceite pela base de dados.
    lote_dados_dict = [item.model_dump(mode='json', exclude_none=True) for item in lote_dados_final]
    lote_dados_json = json.dumps(lote_dados_dict)

    args = (
        usuario_id, data.nomeAlgoritmo, data.versaoAlgoritmo,
        parametros_json, data.dataTreinamento, data.dataExecucao,
        tipos_conteudo_json, lote_dados_json
    )
    
    db_repository.processar_lote_repo(args)
    return {"message": "Lote de resultados processado com sucesso!"}

def salvar_midia(data: ArmazenarMidiaSchema, usuario_id: int):
    args = (
        usuario_id, 
        data.nomeDataset, 
        data.descricaoDataset,
        data.fonteGeral, 
        data.midiaUrl
    )
    db_repository.armazenar_midia_repo(args)
    return {"message": "Mídia armazenada com sucesso!"}

