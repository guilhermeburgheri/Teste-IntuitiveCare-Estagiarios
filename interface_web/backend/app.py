from flask import Flask, jsonify, request
from flask_cors import CORS
import csv
from pathlib import Path
from collections import defaultdict

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

OPERADORAS_CSV = DATA_DIR / "relatorio_cadop.csv"
DESPESAS_CSV = DATA_DIR / "consolidado_despesas.csv"


def only_digits(s: str) -> str:
    return "".join(ch for ch in str(s) if ch.isdigit())

def to_int_digits(value) -> int:
    s = only_digits(value)
    return int(s) if s else 0

def to_float_br(value) -> float:
    if value is None:
        return 0.0

    s = str(value).strip()
    if not s:
        return 0.0

    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")

    try:
        return float(s)
    except ValueError:
        return 0.0


def read_csv_dicts(path: Path, delimiter: str = ",", encoding: str = "utf-8"):
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    with path.open("r", encoding=encoding, newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        rows = []
        for row in reader:
            rows.append({k: (v if v is not None else "") for k, v in row.items()})
        return rows


_CACHE = {"operadoras": None, "despesas": None}


def find_operadora(cnpj_or_registro: str):
    op = load_operadoras()
    key_digits = only_digits(cnpj_or_registro)

    if len(key_digits) >= 11:
        found = op["by_cnpj"].get(key_digits)
        if found:
            return found

    found = op["by_registro"].get(key_digits)
    return found


def load_operadoras():

    if _CACHE["operadoras"] is not None:
        return _CACHE["operadoras"]

    rows = read_csv_dicts(OPERADORAS_CSV, delimiter=";")

    for r in rows:
        r["_registro_norm"] = (r.get("REGISTRO_OPERADORA", "") or "").strip()
        r["_cnpj_norm"] = only_digits(r.get("CNPJ", ""))
        r["_razao_norm"] = (r.get("Razao_Social", "") or "").strip().lower()
    
    by_cnpj = {}
    by_registro = {}
    for r in rows:
        if r["_cnpj_norm"]:
            by_cnpj[r["_cnpj_norm"]] = r
        if r["_registro_norm"]:
            by_registro[r["_registro_norm"]] = r

    data = {
        "rows": rows,
        "col_registro": "REGISTRO_OPERADORA",
        "col_cnpj": "CNPJ",
        "col_razao": "Razao_Social",
        "col_uf": "UF",
        "col_modalidade": "Modalidade",
        "by_cnpj": by_cnpj,
        "by_registro": by_registro,

    }
    _CACHE["operadoras"] = data
    return data


def load_despesas():

    if _CACHE["despesas"] is not None:
        return _CACHE["despesas"]

    rows = read_csv_dicts(DESPESAS_CSV, delimiter=",")


    required = ["RegistroANS", "Ano", "Trimestre", "ValorDespesas"]
    cols = list(rows[0].keys()) if rows else []
    for c in required:
        if c not in cols:
            raise RuntimeError(f"CSV de despesas precisa ter coluna {c}. Colunas: {cols}")

    for r in rows:
        r["_registro_norm"] = (r.get("RegistroANS", "") or "").strip()
        r["_valor_num"] = to_float_br(r.get("ValorDespesas", ""))
        r["_ano_num"] = to_int_digits(r.get("Ano"))
        r["_tri_num"] = to_int_digits(r.get("Trimestre"))


    data = {
        "rows": rows,
        "col_registro": "RegistroANS",
        "col_razao": "RazaoSocial",
        "col_ano": "Ano",
        "col_tri": "Trimestre",
        "col_valor": "ValorDespesas",
    }
    _CACHE["despesas"] = data
    return data


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/operadoras")
def listar_operadoras():
    op = load_operadoras()
    rows = op["rows"]

    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    q = (request.args.get("q") or "").strip().lower()
    q_digits = only_digits(q)

    filtered = rows
    if q:
        def match(r):
            by_name = q in (r.get("_razao_norm") or "")
            by_cnpj = q_digits and q_digits in (r.get("_cnpj_norm") or "")
            by_reg = q_digits and q_digits in (r.get("_registro_norm") or "")
            return by_name or by_cnpj or by_reg

        filtered = [r for r in rows if match(r)]

    total = len(filtered)
    start = (page - 1) * limit
    end = start + limit
    page_rows = filtered[start:end]

    data = []
    for r in page_rows:
        rr = dict(r)
        rr.pop("_registro_norm", None)
        rr.pop("_cnpj_norm", None)
        rr.pop("_razao_norm", None)
        data.append(rr)

    return jsonify({"data": data, "page": page, "limit": limit, "total": total})


@app.get("/api/operadoras/<cnpj>")
def detalhe_operadora(cnpj):
    found = find_operadora(cnpj)
    if not found:
        return jsonify({"error": "Operadora não encontrada"}), 404

    rr = dict(found)
    rr.pop("_registro_norm", None)
    rr.pop("_cnpj_norm", None)
    rr.pop("_razao_norm", None)
    return jsonify(rr)


@app.get("/api/operadoras/<cnpj>/despesas")
def despesas_operadora(cnpj):
    found = find_operadora(cnpj)
    if not found:
        return jsonify({"error": "Operadora não encontrada"}), 404

    registro = only_digits(found.get("REGISTRO_OPERADORA", ""))
    desp = load_despesas()

    hist = [r for r in desp["rows"] if r.get("_registro_norm") == registro]
    hist.sort(key=lambda r: (r.get("_ano_num", 0), r.get("_tri_num", 0)))

    data = []
    for r in hist:
        rr = dict(r)
        rr.pop("_registro_norm", None)
        rr.pop("_valor_num", None)
        rr.pop("_ano_num", None)
        rr.pop("_tri_num", None)
        data.append(rr)

    return jsonify({"cnpj": only_digits(found.get("CNPJ", "")), "registro_ans": registro, "data": data})


@app.get("/api/estatisticas")
def estatisticas():
    op = load_operadoras()
    desp = load_despesas()
    rows = desp["rows"]

    if not rows:
        return jsonify({
            "total_despesas": 0.0,
            "media_despesas": 0.0,
            "top_5_operadoras": [],
            "despesas_por_uf": []
        })

    total = sum(r.get("_valor_num", 0.0) for r in rows)
    media = total / len(rows)

    agg = defaultdict(float)
    for r in rows:
        nome = (r.get("RazaoSocial", "") or "").strip()
        if not nome:
            nome = r.get("_registro_norm", "") or "SEM_NOME"
        agg[nome] += r.get("_valor_num", 0.0)

    top5 = sorted(agg.items(), key=lambda x: x[1], reverse=True)[:5]
    top5_list = [{"nome": k, "total": v} for k, v in top5]

    uf_totais = defaultdict(float)
    for r in rows:
        registro = r.get("_registro_norm", "")
        op_row = op["by_registro"].get(registro)
        uf = (op_row.get("UF") if op_row else None) or "SEM_UF"
        uf_totais[uf] += r.get("_valor_num", 0.0)

    despesas_por_uf = [{"uf": uf, "total": val} for uf, val in sorted(uf_totais.items(), key=lambda x: x[1], reverse=True)]

    return jsonify({
        "total_despesas": total,
        "media_despesas": media,
        "top_5_operadoras": top5_list,
        "despesas_por_uf": despesas_por_uf
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
