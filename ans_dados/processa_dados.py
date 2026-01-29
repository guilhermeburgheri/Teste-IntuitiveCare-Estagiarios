import csv
import zipfile
from pathlib import Path

from openpyxl import load_workbook


CHAVES = ("evento", "sinistro")
SAIDAS_ACEITAS = (".csv", ".txt", ".xlsx", ".xlsm")


def extrair_zips(zips_dir: Path, destino: Path) -> None:
    destino.mkdir(parents=True, exist_ok=True)

    for zip_path in zips_dir.glob("*.zip"):
        pasta = destino / zip_path.stem
        pasta.mkdir(exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(pasta)


def tem_evento_sinistro(texto: str) -> bool:
    t = (texto or "").lower()
    return any(k in t for k in CHAVES)


def linhas_csv_ou_txt(path: Path):
    for delim in (";", ",", "\t"):
        try:
            with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
                r = csv.DictReader(f, delimiter=delim)
                if r.fieldnames and len(r.fieldnames) > 1:
                    for row in r:
                        yield row
                    return
        except Exception:
            pass


def linhas_xlsx(path: Path):
    wb = load_workbook(path, read_only=True, data_only=True)
    for ws in wb.worksheets:
        it = ws.iter_rows(values_only=True)
        try:
            header = next(it)
        except StopIteration:
            continue

        cols = [str(c).strip() if c is not None else "" for c in header]

        for row in it:
            d = {}
            for i, v in enumerate(row):
                if i >= len(cols):
                    break
                d[cols[i]] = "" if v is None else str(v)
            yield d


def contar_arquivos_com_eventos(base_dir: Path) -> int:
    count = 0

    for arq in base_dir.rglob("*"):
        if not arq.is_file():
            continue
        if arq.suffix.lower() not in SAIDAS_ACEITAS:
            continue

        try:
            if arq.suffix.lower() in (".csv", ".txt"):
                linhas = linhas_csv_ou_txt(arq)
            else:
                linhas = linhas_xlsx(arq)

            achou = False
            for row in linhas:
                if any(tem_evento_sinistro(v) for v in row.values()):
                    achou = True
                    break

            if achou:
                count += 1

        except Exception:
            continue

    return count
