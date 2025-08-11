# backend/schemas/search_schemas.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class PesquisaAvancadaSchema(BaseModel):
 
    # Schema for validating the advanced search filters for 'Lotes with Results'.
    # All fields are optional, matching the flexibility of the search form presented in the screens.
    
    textoLivre: Optional[str] = None
    nomeAlgoritmo: Optional[str] = None
    versaoAlgoritmo: Optional[str] = None
    parametrosAlgoritmoQuery: Optional[str] = None
    confiancaMin: Optional[float] = None
    confiancaMax: Optional[float] = None
    scoreMin: Optional[float] = None
    scoreMax: Optional[float] = None
    categoriaDetectada: Optional[str] = None
    fonteConteudo: Optional[str] = None
    categoriaInicial: Optional[str] = None
    metadadosConteudoQuery: Optional[str] = None
    tiposConteudoJSON: Optional[List[str]] = None
    dataPublicacaoInicio: Optional[date] = None
    dataPublicacaoFim: Optional[date] = None
    dataExecucaoInicio: Optional[datetime] = None
    dataExecucaoFim: Optional[datetime] = None
    dataTreinamentoInicio: Optional[date] = None
    dataTreinamentoFim: Optional[date] = None
    nomeUploader: Optional[str] = None

class PesquisarMidiaSchema(BaseModel):
    """
    Schema for validating the search filters for 'Lotes de Mídia Armazenada'.
    """
    textoLivre: Optional[str] = None
    nomeDataset: Optional[str] = None
    fonte: Optional[str] = None
    tiposConteudoJSON: Optional[List[str]] = None
    nomeUploader: Optional[str] = None
