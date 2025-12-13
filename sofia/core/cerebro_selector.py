"""
🌸 Sofia - Seletor de Cérebro
Escolhe dinamicamente entre Ollama (local) ou GitHub Models (cloud)
com suporte a troca em tempo real via API
"""

import os
import sys
import importlib.util
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable

# Importar ambos os cérebros
# Obs: `sofia.core.__init__` expõe `cerebro` como alias do seletor.
# Para evitar recursão no modo LOCAL, carregamos o módulo local diretamente do arquivo.
def _carregar_cerebro_local():
    nome_mod = "sofia.core._cerebro_local_impl"
    existente = sys.modules.get(nome_mod)
    if existente is not None:
        return existente

    caminho = Path(__file__).with_name("cerebro.py")
    spec = importlib.util.spec_from_file_location(nome_mod, str(caminho))
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível carregar o cérebro local em {caminho}")

    mod = importlib.util.module_from_spec(spec)
    # Garante que imports relativos dentro do cérebro local funcionem.
    mod.__package__ = __package__
    sys.modules[nome_mod] = mod
    spec.loader.exec_module(mod)
    return mod


cerebro_local = _carregar_cerebro_local()
from . import cerebro_cloud

# Estado do modo - pode ser alterado em runtime
_current_mode = None

def _detect_initial_mode():
    """Detecta o modo inicial baseado nas variáveis de ambiente"""
    use_cloud = os.getenv("SOFIA_USE_CLOUD", "false").lower() == "true"
    github_token = os.getenv("GITHUB_TOKEN", "")
    return "cloud" if (use_cloud or github_token) else "local"

def get_mode():
    """Retorna o modo atual (cloud ou local)"""
    global _current_mode
    if _current_mode is None:
        _current_mode = _detect_initial_mode()
    return _current_mode

def set_mode(mode: str):
    """Define o modo (cloud ou local)"""
    global _current_mode
    if mode not in ("cloud", "local"):
        raise ValueError("Modo deve ser 'cloud' ou 'local'")
    _current_mode = mode
    print(f"Sofia alterou para modo {'CLOUD (GitHub Models)' if mode == 'cloud' else 'LOCAL (Ollama)'}")
    return _current_mode

def perguntar(
    texto: str,
    historico: Optional[List[Dict[str, Any]]] = None,
    usuario: str = "",
    cancel_callback: Optional[Callable[[], bool]] = None,
    profile_id: Optional[str] = None,
    *,
    progress_callback: Optional[Callable[[str, str], None]] = None,
) -> str:
    """
    Função principal - roteia para o cérebro apropriado
    baseado no modo atual.
    
    Mantém a mesma assinatura do cerebro.py (local) para compatibilidade.
    Adapta os parâmetros para cerebro_cloud quando necessário.
    """
    mode = get_mode()
    
    if mode == "cloud":
        # Adaptar para assinatura do cerebro_cloud
        # cerebro_cloud usa: (texto, contexto, modelo, imagens, metadata_extra)
        metadata_extra = {
            "usuario": usuario or "Usuário",
            "profile_id": profile_id,
        }
        # Converter histórico para contexto string se existir
        contexto = None
        if historico:
            contexto = "\n".join([
                f"{msg.get('de', 'Usuário')}: {msg.get('texto', '')}" 
                for msg in historico[-5:]  # Últimas 5 mensagens
            ])
        return cerebro_cloud.perguntar(texto, contexto=contexto, metadata_extra=metadata_extra)
    else:
        # Local usa a assinatura completa
        return cerebro_local.perguntar(
            texto,
            historico,
            usuario,
            cancel_callback,
            profile_id,
            progress_callback=progress_callback,
        )

# Inicializar e mostrar modo
_current_mode = _detect_initial_mode()
print(f"Sofia iniciou em modo {'CLOUD (GitHub Models)' if _current_mode == 'cloud' else 'LOCAL (Ollama)'}")

# Exportar
__all__ = ['perguntar', 'get_mode', 'set_mode']
