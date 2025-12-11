"""
Sofia - Core simplificado

Expõe o cérebro via seletor para permitir alternar entre
modo local (Ollama) e modo cloud (GitHub Models) com base
nas variáveis de ambiente.
"""

from . import identidade
from . import memoria
from . import cerebro_selector as cerebro  # faz o switch Cloud/Local

__version__ = "1.0.0"
__author__ = "SomBRaRCP"