"""Profiles cognitivos da Sofia (control plane acima do LLM).

Um Profile governa:
- Políticas de seleção de contexto/memória (TSMP/GMAR-TRQ)
- Modulação curta do prompt (tom/rigor/tolerância a especulação)
- Estado-base simbólico (sinais heurísticos, sem física)

Profile → Metadata → TSMP (gate) → Prompt (estilo) → LLM

Regras:
- Profile ≠ memória
- Profile ≠ prompt longo
- Profile = política + estilo (rápido, reversível, explícito)
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional, Tuple, Iterable


TRQ_DURO: Dict[str, Any] = {
    "id": "trq_duro",
    "descricao": "Isolamento teórico e rigor máximo",
    "tsmp": {
        "modo_trq_duro": True,
        "top_k": 4,
        "max_chars": 1400,
        "fontes_permitidas": {"teorias_cientificas", "subitemotions"},
        "pesos": {"teorias": 1.0, "subitemotions": 0.7, "conversa": 0.0},
    },
    "prompt": {"tom": "analítico", "rigor": "alto", "especulacao": "baixa"},
    "estado_base": {
        "estado": "R",
        "ressonancia": 0.8,
        "curvatura_trq": 1.3,
        "ajuste_trq": "rigor",
    },
}

EXPLORATORIO: Dict[str, Any] = {
    "id": "exploratorio",
    "descricao": "Exploração guiada com controle",
    "tsmp": {
        "modo_trq_duro": False,
        "top_k": 8,
        "max_chars": 2200,
        "fontes_permitidas": {"teorias_cientificas", "subitemotions", "conversa/recente"},
        "pesos": {"teorias": 0.8, "subitemotions": 0.6, "conversa": 0.4},
    },
    "prompt": {"tom": "exploratório", "rigor": "médio", "especulacao": "média"},
    "estado_base": {
        "estado": "A",
        "ressonancia": 0.6,
        "curvatura_trq": 0.9,
        "ajuste_trq": "explorar",
    },
}

CONVERSACIONAL: Dict[str, Any] = {
    "id": "conversacional",
    "descricao": "Diálogo fluido e contextual",
    "tsmp": {
        "modo_trq_duro": False,
        "top_k": 10,
        "max_chars": 3000,
        "fontes_permitidas": {"conversa/recente", "conversa/arquivo", "subitemotions"},
        "pesos": {"teorias": 0.3, "subitemotions": 0.6, "conversa": 0.9},
    },
    "prompt": {"tom": "conversacional", "rigor": "baixo", "especulacao": "média"},
    "estado_base": {
        "estado": "S",
        "ressonancia": 0.5,
        "curvatura_trq": 0.4,
        "ajuste_trq": "dialogo",
    },
}

DEBUG: Dict[str, Any] = {
    "id": "debug",
    "descricao": "Auditoria do TSMP",
    "tsmp": {
        "modo_trq_duro": False,
        "top_k": 12,
        "max_chars": 3500,
        "fontes_permitidas": {"*"},
        "pesos": {"teorias": 0.5, "subitemotions": 0.5, "conversa": 0.5},
        "debug": True,
    },
    "prompt": {"tom": "técnico", "rigor": "alto", "especulacao": "baixa"},
    "estado_base": {
        "estado": "N",
        "ressonancia": 0.2,
        "curvatura_trq": 0.0,
        "ajuste_trq": "auditoria",
    },
}


PROFILES: Dict[str, Dict[str, Any]] = {
    "trq_duro": TRQ_DURO,
    "exploratorio": EXPLORATORIO,
    "conversacional": CONVERSACIONAL,
    "debug": DEBUG,
}

DEFAULT_PROFILE_ID = "conversacional"


def _norm_profile_id(profile_id: Optional[str]) -> Optional[str]:
    if not profile_id:
        return None
    return str(profile_id).strip().lower() or None


def resolver_profile_id(profile_id: Optional[str] = None) -> str:
    """Resolve o profile com precedência: arg → env → default."""
    pid = _norm_profile_id(profile_id)
    if pid and pid in PROFILES:
        return pid

    env_pid = _norm_profile_id(os.getenv("SOFIA_PROFILE", ""))
    if env_pid and env_pid in PROFILES:
        return env_pid

    # Compatibilidade: variável antiga (toggle TRQ duro)
    if os.getenv("SOFIA_TRQ_DURO", "0").strip() == "1":
        return "trq_duro"

    return DEFAULT_PROFILE_ID


def get_profile(profile_id: Optional[str] = None) -> Dict[str, Any]:
    pid = resolver_profile_id(profile_id)
    return PROFILES[pid]


def aplicar_profile(profile_id: Optional[str] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Retorna (profile, metadata_base)"""
    profile = get_profile(profile_id)
    md = dict(profile.get("estado_base") or {})

    tsmp = profile.get("tsmp") or {}
    md["modo_trq_duro"] = bool(tsmp.get("modo_trq_duro") is True)

    # Sinal opcional para auditoria
    if bool(tsmp.get("debug") is True):
        md["tsmp_debug"] = True

    return profile, md


def tsmp_politicas(profile: Dict[str, Any]) -> Dict[str, Any]:
    tsmp = dict(profile.get("tsmp") or {})

    # Normalizar fontes_permitidas para set
    fontes = tsmp.get("fontes_permitidas")
    if isinstance(fontes, (list, tuple, set)):
        tsmp["fontes_permitidas"] = set(str(x) for x in fontes)
    elif fontes is None:
        tsmp["fontes_permitidas"] = None
    else:
        tsmp["fontes_permitidas"] = {str(fontes)}

    # Normalizar pesos
    pesos = tsmp.get("pesos")
    if not isinstance(pesos, dict):
        pesos = {}
    tsmp["pesos"] = {str(k): float(v) for k, v in pesos.items() if v is not None}

    # Defaults seguros
    tsmp.setdefault("top_k", 8)
    tsmp.setdefault("max_chars", 2200)
    tsmp.setdefault("modo_trq_duro", False)
    tsmp.setdefault("debug", False)

    return tsmp


def prompt_diretrizes(profile: Dict[str, Any], metadata: Dict[str, Any]) -> str:
    """Linha curta de diretrizes para modulação do prompt."""
    p = profile.get("prompt") or {}
    tom = str(p.get("tom") or "").strip() or "conversacional"
    rigor = str(p.get("rigor") or "").strip() or "médio"
    esp = str(p.get("especulacao") or "").strip() or "média"

    estado = str(metadata.get("estado") or "").strip() or "-"
    try:
        r = float(metadata.get("ressonancia") or 0.0)
        r_txt = f"{r:.2f}"
    except Exception:
        r_txt = "-"

    return f"Perfil={profile.get('id')} | Tom={tom} | Rigor={rigor} | Especulação={esp} | Estado={estado} (R={r_txt})"


def fontes_permitidas(profile: Dict[str, Any]) -> Optional[set[str]]:
    tsmp = tsmp_politicas(profile)
    fontes = tsmp.get("fontes_permitidas")
    if fontes is None:
        return None
    if "*" in fontes:
        return {"*"}
    return set(fontes)


def pesos_tsmp(profile: Dict[str, Any]) -> Dict[str, float]:
    tsmp = tsmp_politicas(profile)
    return dict(tsmp.get("pesos") or {})


def topk_maxchars(profile: Dict[str, Any]) -> Tuple[int, int]:
    tsmp = tsmp_politicas(profile)
    return int(tsmp.get("top_k") or 8), int(tsmp.get("max_chars") or 2200)


def debug_tsmp(profile: Dict[str, Any]) -> bool:
    tsmp = tsmp_politicas(profile)
    return bool(tsmp.get("debug") is True)
