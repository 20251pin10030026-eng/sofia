import json
import re
import shutil
from datetime import datetime
from pathlib import Path


def sanitizar_conversas(path: Path) -> tuple[int, Path]:
    backup = path.with_suffix(path.suffix + ".bak-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    shutil.copy2(path, backup)

    data = json.loads(path.read_text(encoding="utf-8"))
    conversas = data.get("conversas", [])

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

    redacted_text = "[CONTEÚDO REMOVIDO]"

    count = 0
    for item in conversas:
        texto = item.get("texto")
        if isinstance(texto, str) and rx.search(texto):
            item["texto"] = redacted_text
            if "tamanho" in item:
                item["tamanho"] = len(redacted_text)
            count += 1

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return count, backup


def main() -> None:
    default_path = Path(r"D:\A.I_GitHUB\sofia\.sofia_internal\memoria\conversas.json")
    count, backup = sanitizar_conversas(default_path)
    print(f"Sanitizado: {count} registro(s) com referência sexual.")
    print(f"Backup criado em: {backup}")


if __name__ == "__main__":
    main()
