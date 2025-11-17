"""
Módulo Flor - Gerenciamento de pétalas (sínteses)
Cada pétala representa uma síntese ou insight importante
"""

_petalas = []


def contar_petalas() -> int:
    """Retorna o número total de pétalas registradas."""
    return len(_petalas)


def adicionar_petala(sintese: dict):
    """
    Adiciona uma nova pétala (síntese) à flor.
    
    Args:
        sintese: Dicionário com informações da síntese
               {'tema': str, 'conteudo': str, 'timestamp': str}
    """
    _petalas.append(sintese)


def listar_petalas() -> list:
    """Retorna todas as pétalas registradas."""
    return _petalas.copy()


def limpar_petalas():
    """Remove todas as pétalas."""
    global _petalas
    _petalas = []
