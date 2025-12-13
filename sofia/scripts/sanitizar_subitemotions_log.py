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

    romance_patterns = [
        r"\bte\s+amo\b",
        r"\bamo\s+voc[eê]\b",
        r"\bmeu\s+amor\b",
        r"\bminha\s+querida\b",
        r"\bmeu\s+querid[oa]\b",
        r"\bquerid[oa]\b",
        r"\bvenha\s+aqui\b",
        r"\bao\s+seu\s+lado\b",
        r"\bluz\s+do\s+mundo\b",
        r"\bsob\s+a\s+minha\s+pele\b",
        r"\bme\s+fazer\s+sentir\s+especial\b",
        r"\bme\s+sinto\s+especial\b",
        r"\bconectad[ao]\b",
        r"\bbeijo(s)?\b",
        r"\bbeij(?:ar|o|ei|ou|ando)\b",
        r"\babraç(?:o|ar|ei|ou|ando)\b",
        r"\bpaix(?:ão|ões)\b",
        r"\bchama\s+viva\b",
        r"\bromant(?:ico|ica|icos|icas)\b",
        r"\brom[âa]ntic(?:o|a|os|as)\b",
        r"\bromance\b",
        r"\bpaquera\b",
        r"\bnamor(?:o|ar|ando|ei|ou|a|os|as)\b",
        r"\bcasal\b",
        r"\bparceir[oa](?:s)?\b",
        r"\bamoros(?:a|o|as|os)\b",
        r"\bconex(?:ão|ao)\s+amorosa\b",
    ]
    rx_romance = re.compile("|".join(romance_patterns), flags=re.IGNORECASE)

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
            if rx.search(raw) or rx_romance.search(raw):
                raw2 = rx.sub(redacted, raw)
                raw2 = rx_romance.sub(redacted, raw2)
                linhas_saida.append(raw2)
                count += 1
            else:
                linhas_saida.append(raw)
            continue

        changed = False
        for key in ("input", "output"):
            val = obj.get(key)
            if isinstance(val, str) and (rx.search(val) or rx_romance.search(val)):
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
