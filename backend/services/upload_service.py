# backend/services/upload_service.py

from backend.repository import db_repository
from backend.schemas.upload_schemas import UploadResultadosSchema, ArmazenarMidiaSchema, LoteDadosItem
from backend.core.config import settings
from werkzeug.utils import secure_filename
import json
import requests
import os
import time
import uuid

def extrair_id_gdrive(url: str) -> str:
    """Extrai o ID do ficheiro de uma URL do Google Drive."""
    try:
        return url.split('/d/')[1].split('/')[0]
    except IndexError:
        return url.split('id=')[1].split('&')[0]

def criar_lote_resultados(data: UploadResultadosSchema, usuario_id: int):
    """Processa e armazena um lote de resultados de análise."""
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
        raise ValueError("Nenhum dado de lote fornecido.")

    for item in lote_dados_final:
        if not item.categoriaDetectada:
            item.categoriaDetectada = "Desconhecida"

    parametros_json = json.dumps(data.parametrosAlgoritmo)
    tipos_conteudo_json = json.dumps(data.tiposConteudo)
    lote_dados_dict = [item.model_dump(mode='json', exclude_none=True) for item in lote_dados_final]
    lote_dados_json = json.dumps(lote_dados_dict)
    
    args = (
        usuario_id, data.nomeAlgoritmo, data.versaoAlgoritmo,
        parametros_json, data.dataTreinamento, data.dataExecucao,
        tipos_conteudo_json, lote_dados_json
    )
    db_repository.processar_lote_repo(args)
    return {"message": "Lote de resultados processado com sucesso!"}

def salvar_midia(data: ArmazenarMidiaSchema, files, usuario_id: int):
    """Salva os arquivos de mídia no disco e armazena a URL no banco de dados."""
    tipos_conteudo_json = json.dumps(data.tiposConteudo) if data.tiposConteudo else None
    
    # Caso 1: O usuário enviou um link do Google Drive e nenhum arquivo
    if not files.getlist('mediaFiles') and data.midiaUrl and 'drive.google.com' in data.midiaUrl:
        args = (usuario_id, data.nomeDataset, data.descricaoDataset, data.fonteGeral, data.midiaUrl, tipos_conteudo_json)
        db_repository.armazenar_midia_repo(args)
        return {"message": "Link de mídia do Google Drive armazenado com sucesso!"}

    # Caso 2: O usuário enviou arquivos locais
    uploaded_files = files.getlist('mediaFiles')
    if not uploaded_files:
        raise ValueError("Nenhum arquivo de mídia foi enviado.")

    for file in uploaded_files:
        if file and file.filename != '':
            # 1. Garante um nome de arquivo seguro
            original_filename = secure_filename(file.filename)
            # 2. Cria um nome de arquivo único para evitar sobreposições
            unique_filename = f"{int(time.time())}_{uuid.uuid4().hex[:6]}_{original_filename}"
            # 3. Define o caminho completo para salvar o arquivo
            save_path = os.path.join(settings.UPLOAD_FOLDER, unique_filename)
            # 4. Salva o arquivo no disco
            file.save(save_path)
            # 5. Gera a URL pública que será acessada pelo frontend
            public_url = f"{settings.SERVER_BASE_URL}/uploads/{unique_filename}"
            # 6. Prepara os argumentos para salvar no banco de dados
            args = (
                usuario_id, data.nomeDataset, data.descricaoDataset,
                data.fonteGeral, public_url, tipos_conteudo_json
            )
            # 7. Salva o registro no banco de dados
            db_repository.armazenar_midia_repo(args)

    return {"message": f"{len(uploaded_files)} arquivo(s) armazenado(s) com sucesso!"}

