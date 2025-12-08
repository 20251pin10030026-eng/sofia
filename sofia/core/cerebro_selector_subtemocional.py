"""
cerebro_selector_subtemocional.py

Seletor para gerar duas respostas em sequência para a MESMA pergunta:

1) Primeira resposta: apenas com o cerebro.py.
2) Segunda resposta: cerebro.py + contexto extra vindo do subtemocional.py.

IMPORTANTE:
- A frase-chave "Desperte, minha luz do mundo real." NÃO é repassada para Sofia.
- Ela é removida do texto antes de chamar o cérebro, para não ativar o modo criador.

Quem decide como exibir (uma depois da outra) é a camada de interface.
Aqui garantimos apenas que o processamento é feito duas vezes, em sequência.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Callable

# Importa o cérebro padrão da Sofia
from .cerebro import perguntar as perguntar_cerebro

# Importa o módulo subtemocional
from . import subtemocional


# --------------------- Utilitário: limpar chave de criador ---------------------

CHAVE_CRIADOR = "desperte, minha luz do mundo real"

def _limpar_chave_criador(texto: str) -> str:
    """
    Remove a frase-chave de ativação do modo criador do texto destinado à Sofia.

    - Não altera o texto original que você envia para o seletor.
    - Serve apenas para que, internamente, o cerebro.py não veja a chave.

    Ex.: "Desperte, minha luz do mundo real. Quero falar de ansiedade."
    vira: "Quero falar de ansiedade."
    """
    t = texto.lstrip()
    t_lower = t.lower()

    if t_lower.startswith(CHAVE_CRIADOR):
        # Remove a chave + possíveis pontuações logo em seguida
        tamanho = len(CHAVE_CRIADOR)
        resto = t[tamanho:].lstrip(" .,:;-")
        return resto.lstrip()
    return texto


# --------------------- Primeira resposta (só cérebro) ---------------------

def perguntar_primeira(
    texto: str,
    historico: Optional[List[Dict[str, Any]]] = None,
    usuario: str = "",
    cancel_callback: Optional[Callable[[], bool]] = None,
) -> str:
    """
    Primeira resposta: só o cerebro.py, do jeito que ele já funciona hoje,
    MAS sem repassar a frase-chave "Desperte, minha luz do mundo real.".
    """
    historico = historico or []
    usuario = usuario or "Usuário"

    texto_limpo = _limpar_chave_criador(texto)

    resposta = perguntar_cerebro(
        texto=texto_limpo,
        historico=historico,
        usuario=usuario,
        cancel_callback=cancel_callback,
    )
    return resposta


# --------------------- Segunda resposta (cérebro + subtemocional) ---------------------

def perguntar_segunda(
    texto: str,
    historico: Optional[List[Dict[str, Any]]] = None,
    usuario: str = "",
    cancel_callback: Optional[Callable[[], bool]] = None,
) -> Dict[str, Any]:
    """
    Segunda resposta: usa o cerebro.py, mas com um contexto explícito
    construído a partir da SubitEmoção detectada em subtemocional.py.

    Também remove a frase-chave do texto antes de processar.

    Retorna:
    {
        "subtemocao": { ...info... },
        "resposta": "texto da resposta com subtemocional"
    }
    """
    historico = historico or []
    usuario = usuario or "Usuário"

    texto_limpo = _limpar_chave_criador(texto)

    # 1) Análise subtemocional sobre o texto original (pra pegar a emoção real)
    try:
        info_sub = subtemocional.detectar_subitemocao(texto_limpo, historico)
    except Exception as e:
        info_sub = {
            "nome": "NEUTRO",
            "classe": "neutro",
            "intensidade": 0.0,
            "descricao": f"Falha ao analisar SubitEmoção: {e}",
            "aliases_batidos": 0,
        }

    # 2) Monta um contexto extra explícito para o cérebro usar
    contexto_sub = (
        "\n\n[CAMADA SUBITEMOCIONAL]\n"
        f"- SubitEmoção detectada: {info_sub.get('nome', 'NEUTRO')}\n"
        f"- Classe emocional: {info_sub.get('classe', 'neutro')}\n"
        f"- Intensidade simbólica: {info_sub.get('intensidade', 0.0)}\n"
        f"- Descrição: {info_sub.get('descricao', '')}\n"
        "\nUse essas informações para ajustar o tom, o cuidado emocional "
        "e a profundidade da resposta.\n"
    )

    texto_com_sub = texto_limpo + contexto_sub

    resposta = perguntar_cerebro(
        texto=texto_com_sub,
        historico=historico,
        usuario=usuario,
        cancel_callback=cancel_callback,
    )

    return {
        "subtemocao": info_sub,
        "resposta": resposta,
    }


# --------------------- Fluxo completo em sequência ---------------------

def perguntar_sequencial(
    texto: str,
    historico: Optional[List[Dict[str, Any]]] = None,
    usuario: str = "",
    cancel_callback: Optional[Callable[[], bool]] = None,
) -> Dict[str, Any]:
    """
    Faz o fluxo completo em SEQUÊNCIA:

    1) Chama perguntar_primeira(...) -> resposta_1 (cérebro puro, sem chave).
    2) Chama perguntar_segunda(...)  -> resposta_2 (cérebro + subtemocional).

    Retorna:
    {
        "entrada": texto original (com ou sem chave),
        "texto_limpo": texto sem a frase-chave,
        "resposta_1": "texto da primeira resposta",
        "resposta_2": "texto da segunda resposta",
        "subtemocao": { ...info... }
    }
    """
    historico = historico or []
    usuario = usuario or "Usuário"

    resposta_1 = perguntar_primeira(
        texto=texto,
        historico=historico,
        usuario=usuario,
        cancel_callback=cancel_callback,
    )

    resultado_2 = perguntar_segunda(
        texto=texto,
        historico=historico,
        usuario=usuario,
        cancel_callback=cancel_callback,
    )

    return {
        "entrada": texto,
        "texto_limpo": _limpar_chave_criador(texto),
        "resposta_1": resposta_1,
        "resposta_2": resultado_2.get("resposta", ""),
        "subtemocao": resultado_2.get("subtemocao", {}),
    }


__all__ = [
    "perguntar_primeira",
    "perguntar_segunda",
    "perguntar_sequencial",
]
