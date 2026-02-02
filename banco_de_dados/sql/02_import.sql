DROP TABLE IF EXISTS stg_operadoras;
DROP TABLE IF EXISTS stg_consolidadas;
DROP TABLE IF EXISTS stg_agregadas;


CREATE TABLE stg_operadoras (
  registro_ans  TEXT,
  cnpj          TEXT,
  razao_social  TEXT,
  modalidade    TEXT,
  uf            TEXT
);

CREATE TABLE stg_consolidadas (
  cnpj           TEXT,
  razao_social   TEXT,
  trimestre      TEXT,
  ano            TEXT,
  valor_despesas TEXT
);

CREATE TABLE stg_agregadas (
  razao_social     TEXT,
  uf               TEXT,
  total_despesas   TEXT,
  media_trimestral TEXT,
  desvio_padrao    TEXT,
  extra            TEXT
);


TRUNCATE stg_operadoras;
\copy stg_operadoras (registro_ans, cnpj, razao_social, modalidade, uf) FROM '/data/relatorio_cadop_reduzido.csv' WITH (FORMAT csv, HEADER true, DELIMITER ';', QUOTE '"', ENCODING 'UTF8');

TRUNCATE stg_consolidadas;
COPY stg_consolidadas
FROM '/data/consolidado_despesas.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', QUOTE '"', ENCODING 'UTF8');

TRUNCATE stg_agregadas;
COPY stg_agregadas
FROM '/data/despesas_agregadas.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', QUOTE '"', ENCODING 'UTF8');


INSERT INTO operadoras (cnpj, razao_social, registro_ans, modalidade, uf)
SELECT
  regexp_replace(trim(cnpj), '\D', '', 'g'),
  trim(razao_social),
  NULLIF(trim(registro_ans), ''),
  NULLIF(trim(modalidade), ''),
  NULLIF(trim(uf), '')
FROM stg_operadoras
WHERE cnpj IS NOT NULL AND trim(cnpj) <> ''
ON CONFLICT (cnpj) DO NOTHING;


INSERT INTO operadoras (cnpj, razao_social)
SELECT
  regexp_replace(trim(cnpj), '\D', '', 'g'),
  COALESCE(NULLIF(trim(razao_social), ''), 'RAZAO_SOCIAL_NAO_INFORMADA')
FROM stg_consolidadas sc
WHERE sc.cnpj IS NOT NULL AND trim(sc.cnpj) <> ''
ON CONFLICT (cnpj) DO NOTHING;


INSERT INTO despesas_consolidadas (cnpj, razao_social, ano, trimestre, valor_despesas)
SELECT
  regexp_replace(trim(cnpj), '\D', '', 'g') AS cnpj_limpo,
  COALESCE(NULLIF(trim(razao_social), ''), 'RAZAO_SOCIAL_NAO_INFORMADA'),
  CAST(NULLIF(trim(ano), '') AS SMALLINT),
  CAST(NULLIF(replace(upper(trim(trimestre)), 'T', ''), '') AS SMALLINT),
  CAST(replace(replace(NULLIF(trim(valor_despesas), ''), '.', ''), ',', '.') AS NUMERIC(18,2))
FROM stg_consolidadas
WHERE cnpj IS NOT NULL AND trim(cnpj) <> '';


INSERT INTO despesas_agregadas (razao_social, uf, total_despesas, media_trimestral, desvio_padrao)
SELECT
  trim(razao_social),
  trim(uf),
  CAST(replace(replace(NULLIF(trim(total_despesas), ''), '.', ''), ',', '.') AS NUMERIC(18,2)),
  CAST(replace(replace(NULLIF(trim(media_trimestral), ''), '.', ''), ',', '.') AS NUMERIC(18,2)),
  CAST(replace(replace(NULLIF(trim(desvio_padrao), ''), '.', ''), ',', '.') AS NUMERIC(18,2))
FROM stg_agregadas
WHERE razao_social IS NOT NULL AND trim(razao_social) <> '';
