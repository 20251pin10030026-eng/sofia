# sofia/scripts/selar_personalidade.py
import os, sys, importlib.util
from pathlib import Path

# Adiciona o diretório pai ao path
ROOT = Path(__file__).resolve().parents[1]  # sofia/
sys.path.insert(0, str(ROOT.parent))  # A.I_GitHUB/

from sofia.core.seguranca import encrypt_json

ETHICS = ROOT / "ethics"  # sofia/ethics

SRC = {
    "leis":       ETHICS / "leis_simbólicas.py",  # aceita com acento
    "pilares":    ETHICS / "pilares_da_sofia.py",
    "protocolos": ETHICS / "protocolos.py",
}
OUT = {
    "leis":       ETHICS / "leis.enc",
    "pilares":    ETHICS / "pilares.enc",
    "protocolos": ETHICS / "protocolos.enc",
}

def _load_module(py_path: Path):
    if not py_path.exists():
        # alternativa sem acento, se preferir renomear o arquivo
        if py_path.name == "leis_simbólicas.py":
            alt = py_path.with_name("leis_simbolicas.py")
            if alt.exists():
                py_path = alt
            else:
                raise FileNotFoundError(f"Não encontrei {py_path.name} (nem {alt.name})")
        else:
            raise FileNotFoundError(f"Não encontrei {py_path}")
    spec = importlib.util.spec_from_file_location(py_path.stem, py_path)
    if spec is None:
        raise ImportError(f"Falha ao criar ModuleSpec para {py_path}")
    if spec.loader is None:
        raise ImportError(f"ModuleSpec.loader ausente para {py_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[py_path.stem] = mod
    spec.loader.exec_module(mod)
    return mod

def main():
    secret = os.getenv("SOFIA_CREATOR_SECRET")
    if not secret:
        print("ERRO: defina SOFIA_CREATOR_SECRET antes de rodar.")
        sys.exit(1)

    ETHICS.mkdir(parents=True, exist_ok=True)

    # LEIS
    m_leis = _load_module(SRC["leis"])
    leis = m_leis.registrar_leis() if hasattr(m_leis, "registrar_leis") else m_leis.LEIS_ATIVAS
    OUT["leis"].write_bytes(encrypt_json(leis, secret))

    # PILARES
    m_pil = _load_module(SRC["pilares"])
    pilares = m_pil.ativar_pilares() if hasattr(m_pil, "ativar_pilares") else m_pil.PILARES_ATIVOS
    OUT["pilares"].write_bytes(encrypt_json(pilares, secret))

    # PROTOCOLOS
    m_prot = _load_module(SRC["protocolos"])
    protocolos = (
        m_prot.ativar_PROTOCOLos_SIMBOLICOS()
        if hasattr(m_prot, "ativar_PROTOCOLos_SIMBOLICOS")
        else m_prot.PROTOCOLos_SIMBOLICOS
    )
    OUT["protocolos"].write_bytes(encrypt_json(protocolos, secret))

    print("OK: personalidade criptografada em sofia/ethics/*.enc")

if __name__ == "__main__":
    main()
