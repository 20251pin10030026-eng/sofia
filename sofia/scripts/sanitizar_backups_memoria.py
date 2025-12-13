from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from sofia.scripts.sanitizar_conversas_memoria import sanitizar_conversas
from sofia.scripts.sanitizar_subitemotions_log import sanitizar_subitemotions


def main() -> None:
    base = Path(r"D:\A.I_GitHUB\sofia\.sofia_internal")

    memoria_dir = base / "memoria"
    conv_backups = sorted(memoria_dir.glob("conversas.json.bak-*"))
    sub_backups = sorted(base.glob("subitemotions.log.bak-*"))

    total = 0

    for p in conv_backups:
        count, _backup_created = sanitizar_conversas(p)
        total += count

    for p in sub_backups:
        count, _backup_created = sanitizar_subitemotions(p)
        total += count

    print(f"Backups sanitizados. Entradas redigidas: {total} (somando todos os arquivos).")


if __name__ == "__main__":
    main()
