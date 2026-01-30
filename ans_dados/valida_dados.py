import csv
import re
from pathlib import Path


def so_digitos(s: str) -> str:
    return re.sub(r"\D+", "", s or "")


def cnpj_valido(cnpj_raw: str) -> bool:
    cnpj = so_digitos(cnpj_raw)

    if len(cnpj) != 14:
        return False
    if cnpj == cnpj[0] * 14:
        return False

    def calc_dv(base: str, pesos: list[int]) -> str:
        soma = sum(int(d) * p for d, p in zip(base, pesos))
        resto = soma % 11
        return "0" if resto < 2 else str(11 - resto)

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    dv1 = calc_dv(cnpj[:12], pesos1)
    dv2 = calc_dv(cnpj[:12] + dv1, pesos2)
    return cnpj[-2:] == dv1 + dv2


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


def validar_dados(consolidado_csv: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    validado_csv = out_dir / "consolidado_validado.csv"
    erros_csv = out_dir / "erros_validacao.csv"

    with consolidado_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []

        campos = {"RegistroANS", "RazaoSocial", "Trimestre", "Ano", "ValorDespesas"}
        if not reader.fieldnames or not campos.issubset(reader.fieldnames):
            raise ValueError(f"CSV inválido, colunas esperadas: {campos}")
        
        tem_cnpj = "CNPJ" in fieldnames

        campos_saida = fieldnames + [
            "StatusValor",
            "StatusRazaoSocial",
        ]
        if tem_cnpj:
            campos_saida.append("StatusCNPJ")

        with validado_csv.open("w", encoding="utf-8", newline="") as fv, erros_csv.open(
            "w", encoding="utf-8", newline=""
        ) as fe:

            w_valid = csv.DictWriter(fv, fieldnames=campos_saida)
            w_valid.writeheader()

            w_err = csv.DictWriter(
                fe,
                fieldnames=["Linha", "Campo", "Erro", "Valor"],
            )
            w_err.writeheader()

            for linha, row in enumerate(reader, start=2):
                razao = (row.get("RazaoSocial") or "").strip()
                valor_raw = row.get("ValorDespesas")

                valor = parse_float(valor_raw)
                if valor is None:
                    row["StatusValor"] = "INVALIDO"
                    w_err.writerow(
                        {
                            "Linha": linha,
                            "Campo": "ValorDespesas",
                            "Erro": "VALOR_NAO_NUMERICO",
                            "Valor": valor_raw,
                        }
                    )
                elif valor <= 0:
                    row["StatusValor"] = "INVALIDO"
                    w_err.writerow(
                        {
                            "Linha": linha,
                            "Campo": "ValorDespesas",
                            "Erro": "VALOR_NAO_POSITIVO",
                            "Valor": valor_raw,
                        }
                    )
                else:
                    row["StatusValor"] = "OK"


                if razao:
                    row["StatusRazaoSocial"] = "OK"
                else:
                    row["StatusRazaoSocial"] = "INVALIDO"
                    w_err.writerow(
                        {
                            "Linha": linha,
                            "Campo": "RazaoSocial",
                            "Erro": "RAZAO_SOCIAL_VAZIA",
                            "Valor": razao,
                        }
                    )
                

                if tem_cnpj:
                    cnpj = (row.get("CNPJ") or "").strip()
                    if cnpj_valido(cnpj):
                        row["StatusCNPJ"] = "OK"
                    else:
                        row["StatusCNPJ"] = "INVALIDO"
                        w_err.writerow(
                            {
                                "Linha": linha,
                                "Campo": "CNPJ",
                                "Erro": "CNPJ_INVALIDO",
                                "Valor": cnpj,
                            }
                        )

                w_valid.writerow(row)

    print("Validação concluída!")

if __name__ == "__main__":
    validar_dados(
        Path(".documentos/filtrado/consolidado.csv"),
        Path(".documentos/validacao")
    )
