import csv
import re
import zipfile
from pathlib import Path

from ans_dados.processa_dados import filtrar_eventos_sinistros


def ano_trimestre(path: Path) -> tuple[int | None, str | None]:
    m = re.search(r"([1-4])T(20\d{2})", str(path))
    if not m:
        return None, None
    return int(m.group(2)), f"{m.group(1)}T"


def gerar_finalizado(extracao_dir: Path, cons_dir: Path) -> Path:
    cons_dir.mkdir(parents=True, exist_ok=True)

    soma: dict[tuple[str, int, str], float] = {}
    inconsist = []

    for item in filtrar_eventos_sinistros(extracao_dir):
        arq = Path(item["arquivo"])
        ano, tri = ano_trimestre(arq)
        if ano is None or tri is None:
            inconsist.append({"Tipo": "TRIMESTRE_INVALIDO", "Arquivo": str(arq)})
            continue

        valor = float(item["valor"])
        id_oper = str(item.get("id_operadora") or "").strip()

        if not id_oper:
            inconsist.append({"Tipo": "ID_OPERADORA_VAZIO", "Arquivo": str(arq)})
            continue

        cnpj = id_oper
        razao = ""

        chave = (cnpj, ano, tri)
        soma[chave] = soma.get(chave, 0.0) + valor

        if valor <= 0:
            inconsist.append(
                {
                    "Tipo": "VALOR_ZERO_OU_NEGATIVO",
                    "CNPJ": cnpj,
                    "Ano": ano,
                    "Trimestre": tri,
                    "Valor": valor,
                    "Arquivo": str(arq),
                }
            )

    consolidado = cons_dir / "consolidado.csv"
    with consolidado.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["CNPJ", "RazaoSocial", "Trimestre", "Ano", "ValorDespesas"])
        for (cnpj, ano, tri), total in sorted(soma.items(), key=lambda x: (x[0][1], x[0][2], x[0][0])):
            w.writerow([cnpj, razao, tri, ano, f"{total:.2f}"])

    if inconsist:
        vistos = set()
        unicas = []
        for d in inconsist:
            chave = tuple(sorted((k, str(v)) for k, v in d.items()))
            if chave not in vistos:
                vistos.add(chave)
                unicas.append(d)

        inc = cons_dir / "inconsistencias.csv"
        cols = sorted({k for d in unicas for k in d.keys()})
        with inc.open("w", encoding="utf-8", newline="") as f:
            dw = csv.DictWriter(f, fieldnames=cols)
            dw.writeheader()
            dw.writerows(unicas)
    
    return consolidado 


def zipar_finalizado(consolidado_csv: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.write(consolidado_csv, arcname=consolidado_csv.name)
