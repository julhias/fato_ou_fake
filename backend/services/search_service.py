# backend/services/search_service.py

from backend.repository import db_repository
from backend.schemas.search_schemas import PesquisaAvancadaSchema, PesquisarMidiaSchema
import json

def realizar_pesquisa_avancada(data: PesquisaAvancadaSchema):
    """
    Prepara os argumentos a partir do schema e chama o repositório de pesquisa avançada.
    Agora inclui todos os filtros do protótipo.
    """
    # Converte a lista de tipos de conteúdo para uma string JSON, se existir
    tipos_conteudo = json.dumps(data.tiposConteudoJSON) if data.tiposConteudoJSON else None

    # A ordem dos argumentos DEVE corresponder exatamente à procedure sp_PesquisaAvancada no SQL
    args = (
        data.textoLivre, 
        data.nomeAlgoritmo, 
        data.versaoAlgoritmo,
        data.parametrosAlgoritmoQuery, 
        data.confiancaMin, 
        data.confiancaMax,
        data.scoreMin, 
        data.scoreMax, 
        data.categoriaDetectada,
        data.fonteConteudo, 
        data.categoriaInicial, 
        data.metadadosConteudoQuery,
        tipos_conteudo, 
        data.dataPublicacaoInicio, 
        data.dataPublicacaoFim,
        data.dataExecucaoInicio, 
        data.dataExecucaoFim, 
        data.dataTreinamentoInicio,
        data.dataTreinamentoFim, 
        data.nomeUploader
    )
    
    results = db_repository.pesquisa_avancada_repo(args)
    return results

def realizar_pesquisa_midia(data: PesquisarMidiaSchema):
    """
    Prepara os argumentos e chama o repositório de pesquisa de mídia armazenada.
    """
    tipos_conteudo = json.dumps(data.tiposConteudoJSON) if data.tiposConteudoJSON else None
    
    args = (
        data.textoLivre, 
        data.nomeDataset,
        data.fonte, 
        tipos_conteudo, 
        data.nomeUploader
    )
    
    results = db_repository.pesquisar_midia_repo(args)
    return results
