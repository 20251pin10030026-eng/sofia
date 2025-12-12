import json
import re
import shutil
from datetime import datetime
from pathlib import Path


def sanitizar_subitemotions(path: Path) -> tuple[int, Path]:
    backup = path.with_suffix(path.suffix + ".bak-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    shutil.copy2(path, backup)

    # Padrões para identificar conteúdo sexual. Mantém viés conservador (remove referências diretas).
    patterns = [
        r"\bsexo\b",
        r"\bsexual\b",
        r"\bporn(?:o|ô|ografia|ografico|ográfica|ográfico)?\b",
        r"\bnude(?:z|s)?\b",
        r"\bpelad(?:o|a|os|as|inha|inho)?\b",
        r"\ber[oó]tic(?:o|a|os|as)?\b",
        r"\bfetich(?:e|es|ismo)?\b",
        r"\bmasturb(?:a|ação|ar|ando|ei|ou)?\b",
        r"\btransar\b",
        r"\bcoito\b",
        r"\bconte[úu]do\s+adulto\b",
    ]
    rx = re.compile("|".join(patterns), flags=re.IGNORECASE)

    redacted = "[CONTEÚDO REMOVIDO]"

    linhas_saida: list[str] = []
    count = 0

    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines(True):
        if raw.strip() == "":
            linhas_saida.append(raw)
            continue

        # Primeiro tenta tratar como JSONL válido.
        try:
            obj = json.loads(raw)
        except Exception:
            # Se não for JSON válido, faz substituição direta na linha para não quebrar o arquivo.
            if rx.search(raw):
                linhas_saida.append(rx.sub(redacted, raw))
                count += 1
            else:
                linhas_saida.append(raw)
            continue

        changed = False
        for key in ("input", "output"):
            val = obj.get(key)
            if isinstance(val, str) and rx.search(val):
                obj[key] = redacted
                changed = True

        if changed:
            count += 1

        linhas_saida.append(json.dumps(obj, ensure_ascii=False) + "\n")

    path.write_text("".join(linhas_saida), encoding="utf-8")
    return count, backup


def main() -> None:
    path = Path(r"D:\A.I_GitHUB\sofia\.sofia_internal\subitemotions.log")
    count, backup = sanitizar_subitemotions(path)
    print(f"Sanitizado: {count} linha(s) com referência sexual.")
    print(f"Backup criado em: {backup}")


if __name__ == "__main__":
    main()
