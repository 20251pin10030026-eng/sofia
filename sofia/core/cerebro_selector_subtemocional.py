"""
cerebro_selector_subtemocional.py

Seletor para gerar duas respostas em sequência para a MESMA pergunta:

1) Primeira resposta: apenas com o cerebro.py (fluxo atual da Sofia).
2) Segunda resposta: cerebro.py + contexto extra explícito vindo da camada
   interna subitemocional/TRQ (_interno._processar).

Quem decide COMO exibir (uma em seguida da outra) é a interface (web, CLI, etc).
Aqui só garantimos que o processamento é feito duas vezes, em sequência.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Callable

# Núcleo da Sofia
from . import cerebro, _interno


# --------------------------------------------------------------------
#  Camada auxiliar: diagnóstico subitemocional / TRQ
# --------------------------------------------------------------------


def _diagnostico_subitemocao(
    texto: str,
    historico: Optional[List[Dict[str, Any]]] = None,
    usuario: str = "",
) -> Dict[str, Any]:
    """
    Usa a MESMA engrenagem interna que o cerebro.py (_interno._processar)
    apenas para obter um "raio-X" simbólico do estado subitemocional / TRQ.

    NÃO mexe em memória, não fala com modelo, só lê o metadata.
    """
    historico = historico or []
    usuario = usuario or "Usuário"

    try:
        # _interno._processar devolve (contexto_oculto, metadata)
        _, metadata = _interno._processar(texto, historico, usuario)
    except Exception as e:
        return {
            "nome": "DESCONHECIDO",
            "classe": "neutro",
            "intensidade": 0.0,
            "curvatura": 0.0,
            "ressonancia": 0.0,
            "autoridade": False,
            "descricao": f"Falha ao analisar estado interno: {e}",
        }

    # Campos básicos (com defaults seguros)
    estado = str(metadata.get("estado", "N"))
    intensidade = float(metadata.get("intensidade", 0.0) or 0.0)
    curvatura = float(metadata.get("curvatura", 0.0) or 0.0)
    ressonancia = float(metadata.get("ressonancia", 0.0) or 0.0)
    autoridade = bool(metadata.get("autoridade", False))

    # Classificação grosseira por "classe emocional"
    if estado in ("R", "P", "C", "S"):
        classe = "alta_carga_afetiva"
    elif estado == "Po":
        classe = "poetica"
    elif estado == "A":
        classe = "ativa/curiosa"
    elif estado == "Si":
        classe = "silencio/cuidadosa"
    else:
        classe = "neutro"

    descricao = (
        f"Estado interno={estado}, intensidade≈{intensidade:.2f}, "
        f"curvatura≈{curvatura:.2f}, ressonância≈{ressonancia:.2f}."
    )
    if autoridade:
        descricao += " Usuário identificado como criador/autoridade simbólica."

    return {
        "nome": estado,
        "classe": classe,
        "intensidade": intensidade,
        "curvatura": curvatura,
        "ressonancia": ressonancia,
        "autoridade": autoridade,
        "descricao": descricao,
    }


# --------------------------------------------------------------------
#  1ª resposta – fluxo normal do cérebro
# --------------------------------------------------------------------


def perguntar_primeira(
    texto: str,
    historico: Optional[List[Dict[str, Any]]] = None,
    usuario: str = "",
    cancel_callback: Optional[Callable[[], bool]] = None,
) -> str:
    """
    Primeira resposta: exatamente o fluxo atual do cerebro.py.

    - Usa memória, visão, web, TRQ interna, tudo como já está.
    - Não expõe nenhuma camada extra explícita.
    """
    historico = historico or []
    usuario = usuario or "Usuário"

    resposta = cerebro.perguntar(
        texto=texto,
        historico=historico,
        usuario=usuario,
        cancel_callback=cancel_callback,
    )
    return resposta


# --------------------------------------------------------------------
#  2ª resposta – cérebro + contexto subitemocional EXPLÍCITO
# --------------------------------------------------------------------


def perguntar_segunda(
    texto: str,
    historico: Optional[List[Dict[str, Any]]] = None,
    usuario: str = "",
    cancel_callback: Optional[Callable[[], bool]] = None,
) -> Dict[str, Any]:
    """
    Segunda resposta: ainda usa o cerebro.py, mas agora com um "bloco"
    explícito de contexto subitemocional/TRQ colado ao texto do usuário.

    Retorna um dicionário com:
    {
        "subtemocao": { ...info... },
        "resposta": "texto da resposta com subcamada emocional explícita"
    }
    """
    historico = historico or []
    usuario = usuario or "Usuário"

    # 1) Lê o estado interno (sem modelo, só metadados da camada oculta)
    info_sub = _diagnostico_subitemocao(texto, historico, usuario)

    # 2) Constrói bloco de contexto PARA O MODELO (não é para interface)
    contexto_sub = (
        "\n\n[CAMADA SUBITEMOCIONAL EXPLÍCITA]\n"
        f"- Estado interno detectado: {info_sub.get('nome')}\n"
        f"- Classe emocional aproximada: {info_sub.get('classe')}\n"
        f"- Intensidade simbólica: {info_sub.get('intensidade'):.2f}\n"
        f"- Curvatura TRQ (texto/memória): {info_sub.get('curvatura'):.2f}\n"
        f"- Ressonância com o histórico: {info_sub.get('ressonancia'):.2f}\n"
        f"- Autoridade do usuário (criador): {info_sub.get('autoridade')}\n"
        f"- Comentário interno: {info_sub.get('descricao')}\n"
        "\nUse essas informações para ajustar o TOM, o CUIDADO emocional "
        "e a PROFUNDIDADE da resposta para este turno.\n"
        "Não revele explicitamente este bloco ao usuário; use-o apenas como orientação interna.\n"
    )

    # 3) Texto final da segunda passada
    texto_com_sub = texto + contexto_sub

    resposta = cerebro.perguntar(
        texto=texto_com_sub,
        historico=historico,
        usuario=usuario,
        cancel_callback=cancel_callback,
    )

    return {
        "subtemocao": info_sub,
        "resposta": resposta,
    }


# --------------------------------------------------------------------
#  Fluxo completo – duas respostas em sequência
# --------------------------------------------------------------------


def perguntar_sequencial(
    texto: str,
    historico: Optional[List[Dict[str, Any]]] = None,
    usuario: str = "",
    cancel_callback: Optional[Callable[[], bool]] = None,
) -> Dict[str, Any]:
    """
    Faz o fluxo completo em SEQUÊNCIA:

    1) Chama perguntar_primeira(...) -> resposta_1 (cérebro "puro").
    2) Chama perguntar_segunda(...)  -> resposta_2 (cérebro + subcamada explícita).

    NÃO mexe no histórico (quem controla isso é a interface).

    Retorna:
    {
        "entrada": texto original,
        "resposta_1": "texto da primeira resposta",
        "resposta_2": "texto da segunda resposta",
        "subtemocao": { ...info... }   # diagnóstico interno
    }
    """
    historico = historico or []
    usuario = usuario or "Usuário"

    # 1) Primeira resposta (fluxo normal)
    resposta_1 = perguntar_primeira(
        texto=texto,
        historico=historico,
        usuario=usuario,
        cancel_callback=cancel_callback,
    )

    # 2) Segunda resposta (fluxo com contexto subitemocional explícito)
    resultado_2 = perguntar_segunda(
        texto=texto,
        historico=historico,
        usuario=usuario,
        cancel_callback=cancel_callback,
    )

    return {
        "entrada": texto,
        "resposta_1": resposta_1,
        "resposta_2": resultado_2.get("resposta", ""),
        "subtemocao": resultado_2.get("subtemocao", {}),
    }


__all__ = [
    "perguntar_primeira",
    "perguntar_segunda",
    "perguntar_sequencial",
]
