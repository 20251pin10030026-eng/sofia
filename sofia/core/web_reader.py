"""
web_reader.py
Módulo para Sofia ler páginas web, extrair texto e avaliar se o conteúdo
é relevante para o prompt do usuário.
"""

from __future__ import annotations

import re
from typing import List, Dict, Any, Optional

import requests
from bs4 import BeautifulSoup


# ---------------------------
# 1. Extração de URLs do texto
# ---------------------------

_URL_REGEX = r"(https?://[^\s]+)"


def extrair_urls(texto: str) -> List[str]:
    """Extrai URLs simples de um texto."""
    if not texto:
        return []

    urls = re.findall(_URL_REGEX, texto)
    limpas: List[str] = []
    for u in urls:
        # remove pontuação de cauda comum: ., ), ], ", '
        u_limpa = u.rstrip(".,);]\"'")
        limpas.append(u_limpa)

    # remove duplicadas preservando ordem
    vistas = set()
    uniq = []
    for u in limpas:
        if u not in vistas:
            vistas.add(u)
            uniq.append(u)
    return uniq


# ---------------------------
# 2. Download e limpeza de HTML
# ---------------------------

def baixar_html(url: str, timeout: float = 6.0) -> Optional[str]:
    """Baixa HTML bruto de uma URL. Retorna None em caso de erro."""
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        ctype = resp.headers.get("Content-Type", "")
        if "text/html" not in ctype:
            # ignora PDFs, imagens etc. (isso pode ser expandido depois)
            return None
        return resp.text
    except Exception:
        return None


def extrair_texto(html: str) -> str:
    """
    Limpa o HTML e retorna apenas texto 'legível'.

    Remove script, style, header, footer, nav, form, etc.
    """
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript", "header", "footer",
                     "nav", "form", "aside"]):
        tag.decompose()

    texto = soup.get_text(separator=" ")
    texto = " ".join(texto.split())
    return texto


# ---------------------------
# 3. Métrica simples de relevância
# ---------------------------

_STOPWORDS_PT = {
    "a", "o", "os", "as", "um", "uma", "uns", "umas",
    "de", "da", "do", "das", "dos",
    "e", "é", "em", "no", "na", "nos", "nas",
    "que", "com", "por", "para", "pra", "ser",
    "se", "ao", "aos", "à", "às",
    "como", "onde", "quando", "porque", "porquê",
    "mais", "menos", "muito", "muita", "muitos", "muitas",
    "já", "não", "sim", "tem", "têm", "entre", "sobre",
    "ou", "até", "apenas", "também",
}


def _tokenizar(texto: str) -> List[str]:
    texto = texto.lower()
    tokens = re.findall(r"\b\w+\b", texto, flags=re.UNICODE)
    return [t for t in tokens if t not in _STOPWORDS_PT and len(t) > 2]


def calcular_relevancia(prompt: str, texto_pagina: str) -> float:
    """
    Retorna um score de 0 a 1 baseado na sobreposição de palavras
    (Jaccard simples entre conjuntos de tokens).
    """
    pw = set(_tokenizar(prompt))
    tw = set(_tokenizar(texto_pagina))
    if not pw or not tw:
        return 0.0

    inter = len(pw & tw)
    uniao = len(pw | tw)
    if uniao == 0:
        return 0.0
    return inter / uniao


# ---------------------------
# 4. Pipeline completo
# ---------------------------

def analisar_urls_no_texto(
    prompt: str,
    limiar: float = 0.20,
    max_chars_resumo: int = 2000,
) -> Dict[str, Any]:
    """
    Pipeline completo:
    - extrai URLs do prompt
    - baixa HTML
    - extrai texto
    - calcula relevância vs prompt
    - devolve o melhor resultado e metadados

    Retorno:
        {
          "urls": [...],
          "relevante": bool,
          "melhor_url": str | None,
          "score": float,
          "resumo": str,
          "erro": str | None
        }
    """
    resultado: Dict[str, Any] = {
        "urls": [],
        "relevante": False,
        "melhor_url": None,
        "score": 0.0,
        "resumo": "",
        "erro": None,
    }

    urls = extrair_urls(prompt)
    resultado["urls"] = urls

    if not urls:
        return resultado

    melhor_score = 0.0
    melhor_url: Optional[str] = None
    melhor_texto: str = ""

    for url in urls:
        html = baixar_html(url)
        if not html:
            continue
        texto = extrair_texto(html)
        if not texto:
            continue
        score = calcular_relevancia(prompt, texto)
        if score > melhor_score:
            melhor_score = score
            melhor_url = url
            melhor_texto = texto

    resultado["score"] = float(melhor_score)
    resultado["melhor_url"] = melhor_url

    if melhor_url is None:
        # Nenhuma página útil foi lida
        return resultado

    if melhor_score >= limiar and melhor_texto:
        resultado["relevante"] = True
        if len(melhor_texto) > max_chars_resumo:
            resumo = melhor_texto[:max_chars_resumo] + " ..."
        else:
            resumo = melhor_texto
        resultado["resumo"] = resumo

    return resultado
