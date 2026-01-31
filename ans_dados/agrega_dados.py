import csv
import math
import zipfile
from pathlib import Path


def parse_float(valor: str):
    if valor is None:
        return None
    v = str(valor).strip()
    if not v:
        return None

    if "," in v and "." in v and v.rfind(",") > v.rfind("."):
        v = v.replace(".", "").replace(",", ".")
    else:
        v = v.replace(",", ".")

    try:
        return float(v)
    except ValueError:
        return None


def trimestre_key(ano: str, trimestre: str) -> str:
    return f"{str(ano).strip()}-{str(trimestre).strip()}"


def media(valores: list[float]) -> float:
    return sum(valores) / len(valores) if valores else 0.0


def desvio_padrao_amostral(valores: list[float]) -> float:
    n = len(valores)
    if n <= 1:
        return 0.0
    m = media(valores)
    var = sum((x - m) ** 2 for x in valores) / (n - 1)
    return math.sqrt(var)


def agregar_despesas(
    consolidado_validado_csv: Path,
    out_dir: Path,
    zip_path: Path,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)

    por_grupo_trimestre: dict[tuple[str, str], dict[str, float]] = {}

    with consolidado_validado_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []

        for row in reader:
            if not (row.get("RazaoSocial") or "").strip():
                continue
            if not (row.get("CNPJ") or "").strip():
                continue

            razao = (row.get("RazaoSocial") or "").strip()
            uf = (row.get("UF") or "").strip()
            ano = (row.get("Ano") or "").strip()
            tri = (row.get("Trimestre") or "").strip()

            if not razao or not uf or not ano or not tri:
                continue

            valor = parse_float(row.get("ValorDespesas"))
            if valor is None:
                continue

            g = (razao, uf)
            tkey = trimestre_key(ano, tri)

            por_grupo_trimestre.setdefault(g, {})
            por_grupo_trimestre[g][tkey] = por_grupo_trimestre[g].get(tkey, 0.0) + valor

    linhas = []
    for (razao, uf), mapa_tri in por_grupo_trimestre.items():
        valores_trimestrais = [mapa_tri[k] for k in sorted(mapa_tri.keys())]
        total = sum(valores_trimestrais)
        med = media(valores_trimestrais)
        std = desvio_padrao_amostral(valores_trimestrais)

        linhas.append(
            {
                "RazaoSocial": razao,
                "UF": uf,
                "TotalDespesas": total,
                "MediaTrimestral": med,
                "DesvioPadraoTrimestral": std,
                "QtdTrimestres": len(valores_trimestrais),
            }
        )

    linhas.sort(key=lambda d: d["TotalDespesas"], reverse=True)

    out_csv = out_dir / "despesas_agregadas.csv"
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "RazaoSocial",
                "UF",
                "TotalDespesas",
                "MediaTrimestral",
                "DesvioPadraoTrimestral",
                "QtdTrimestres",
            ],
        )
        w.writeheader()
        for d in linhas:
            d2 = dict(d)
            d2["TotalDespesas"] = f"{d2['TotalDespesas']:.2f}"
            d2["MediaTrimestral"] = f"{d2['MediaTrimestral']:.2f}"
            d2["DesvioPadraoTrimestral"] = f"{d2['DesvioPadraoTrimestral']:.2f}"
            w.writerow(d2)

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.write(out_csv, arcname=out_csv.name)

    return out_csv


if __name__ == "__main__":
    agregar_despesas(
        Path(".documentos/filtrado/consolidado_enriquecido.csv"),
        Path(".documentos/agregado"),
        Path("Teste_GuilhermeBurgheri.zip"),
    )
