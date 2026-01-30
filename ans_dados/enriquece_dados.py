import csv
import requests
from pathlib import Path

URL_CADASTRO = (
    "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv"
)


def baixar_cadastro_se_necessario(cadastro_csv: Path) -> None:
    if cadastro_csv.exists():
        return

    cadastro_csv.parent.mkdir(parents=True, exist_ok=True)

    resp = requests.get(URL_CADASTRO, timeout=60)
    resp.raise_for_status()

    cadastro_csv.write_bytes(resp.content)


def carregar_cadastro(cadastro_csv: Path) -> dict[str, dict]:
    cadastro = {}

    with cadastro_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")

        for row in reader:
            reg = (row.get("REGISTRO_OPERADORA") or "").strip()
            if not reg:
                continue

            if reg not in cadastro:
                cadastro[reg] = {
                    "CNPJ": (row.get("CNPJ") or "").strip(),
                    "RazaoSocial": (row.get("Razao_Social") or "").strip(),
                    "UF": (row.get("UF") or "").strip(),
                    "Modalidade": (row.get("Modalidade") or "").strip(),
                }

    return cadastro


def enriquecer_consolidado(
    consolidado_csv: Path,
    cadastro_csv: Path,
    out_csv: Path,
) -> None:
    baixar_cadastro_se_necessario(cadastro_csv)
    cadastro = carregar_cadastro(cadastro_csv)

    with consolidado_csv.open("r", encoding="utf-8", newline="") as f_in, \
         out_csv.open("w", encoding="utf-8", newline="") as f_out:

        reader = csv.DictReader(f_in)
        campos_saida = reader.fieldnames + ["CNPJ", "UF", "Modalidade"]

        writer = csv.DictWriter(f_out, fieldnames=campos_saida)
        writer.writeheader()

        for row in reader:
            reg = (row.get("RegistroANS") or "").strip()
            dados = cadastro.get(reg)

            if dados:
                row["CNPJ"] = dados["CNPJ"]
                row["RazaoSocial"] = dados["RazaoSocial"]
                row["UF"] = dados["UF"]
                row["Modalidade"] = dados["Modalidade"]
            else:
                row["CNPJ"] = ""
                row["UF"] = ""
                row["Modalidade"] = ""

            writer.writerow(row)


if __name__ == "__main__":
    enriquecer_consolidado(
        Path(".documentos/filtrado/consolidado.csv"),
        Path(".documentos/cadastro/Relatorio_cadop.csv"),
        Path(".documentos/filtrado/consolidado_enriquecido.csv"),
    )
