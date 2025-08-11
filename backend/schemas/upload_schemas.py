# backend/schemas/upload_schemas.py

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import date, datetime

class LoteDadosItem(BaseModel):
    texto: Optional[str] = None
    midiaUrl: Optional[str] = None
    fonte: Optional[str] = None
    dataPublicacao: Optional[date] = None
    metadados: Optional[Dict[str, Any]] = {}
    score: Optional[float] = None
    confianca: Optional[float] = None
    categoriaDetectada: Optional[str] = None
    confiancaRotulo: Optional[float] = None
    justificativa: Optional[str] = None

class UploadResultadosSchema(BaseModel):
    nomeAlgoritmo: str
    versaoAlgoritmo: str
    dataTreinamento: date
    dataExecucao: datetime
    parametrosAlgoritmo: Dict[str, Any]
    tiposConteudo: List[str]
    
    # --- ALTERAÇÃO PRINCIPAL ---
    # Agora, ou recebemos os dados diretamente, ou recebemos uma URL para os ir buscar.
    loteDados: Optional[List[LoteDadosItem]] = None
    gdriveUrl: Optional[str] = None

class ArmazenarMidiaSchema(BaseModel):
    nomeDataset: str
    descricaoDataset: str
    fonteGeral: Optional[str] = None
    midiaUrl: str