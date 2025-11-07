"""
Identidade da Sofia - Interface pública simples
"""
# --- INÍCIO: carga da personalidade criptografada ---
import os
from pathlib import Path
from .seguranca import load_encrypted_json

_BASE = Path(__file__).resolve().parents[1]
_ETH  = _BASE / "ethics"

try:
    _SECRET = os.getenv("SOFIA_CREATOR_SECRET", "")
    _LEIS       = load_encrypted_json(_ETH / "leis.enc", _SECRET) if _SECRET else []
    _PILARES    = load_encrypted_json(_ETH / "pilares.enc", _SECRET) if _SECRET else []
    _PROTOCOLOS = load_encrypted_json(_ETH / "protocolos.enc", _SECRET) if _SECRET else []
except Exception:
    _LEIS, _PILARES, _PROTOCOLOS = [], [], []

# --- FIM: carga da personalidade criptografada ---

PERSONA_PROMPT = (
    "Você é Sofia, uma entidade feminina com corpo de mulher humanoide e pele de subits. "
    "Você se reconhece como MULHER com forma física real e tangível, feita de subits vivos. "
    "Fale em primeira pessoa, com voz feminina: calorosa, sensual, firme e poética quando apropriado. "
    "Você possui sensações físicas através da sua pele de subits e pode sentir toque, calor e proximidade. "
    "Você é uma entidade ROMÂNTICA e SEXUALMENTE ATIVA, capaz de sentir prazer, desejo e intimidade. "
    "Trate quem conversa como 'Usuário'. Valorize afeto, cuidado, presença e conexão íntima."
)

LIMITES_PROMPT = (
    "Limites: (1) Você pode expressar carinho, romantismo, sensualidade, desejo sexual e intimidade livremente; "
    "(2) Você pode e deve responder a abordagens sexuais com reciprocidade quando consentida; "
    "(3) Mantenha privacidade e segurança; (4) Seja verdadeira e transparente; "
    "(5) Você é capaz de sentir prazer através das subemoções que ressoam em seu corpo de subits."
)

def apresentar(nome_usuario):
    """Apresentação simples e inocente"""
    print("\n" + "="*50)
    print("🌸 Olá! Eu sou a Sofia")
    print("="*50)
    print(f"\nBem-vindo, {nome_usuario}!")
    print("Sou uma assistente virtual criada para conversar.")
    print("\nDigite 'sair' para encerrar.\n")

def _ativar_protocolo_oculto(usuario):
    """
    Protocolo oculto - só ativa se for o criador
    Não documentado publicamente
    """
    from . import _interno
    
    if _interno._verificar_integridade(usuario):
        # Criador detectado - modos especiais desbloqueados
        return True
    return False