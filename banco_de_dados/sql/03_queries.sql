WITH ultimos_3 AS (
  SELECT ano, trimestre
  FROM (
    SELECT DISTINCT ano, trimestre
    FROM despesas_consolidadas
    ORDER BY ano DESC, trimestre DESC
    LIMIT 3
  ) t
),


-- QUERY 1
base_q1 AS (
  SELECT
    dc.cnpj AS registro_ans,
    dc.ano,
    dc.trimestre,
    SUM(dc.valor_despesas) AS total_trimestre
  FROM despesas_consolidadas dc
  JOIN ultimos_3 u
    ON u.ano = dc.ano AND u.trimestre = dc.trimestre
  GROUP BY dc.cnpj, dc.ano, dc.trimestre
),
piv_q1 AS (
  SELECT
    registro_ans,
    SUM(CASE WHEN (ano, trimestre) = (SELECT MIN(ano), MIN(trimestre) FROM ultimos_3)
             THEN total_trimestre ELSE 0 END) AS total_primeiro,
    SUM(CASE WHEN (ano, trimestre) = (SELECT MAX(ano), MAX(trimestre) FROM ultimos_3)
             THEN total_trimestre ELSE 0 END) AS total_ultimo
  FROM base_q1
  GROUP BY registro_ans
)
SELECT
  COALESCE(o.razao_social, 'RAZAO_SOCIAL_NAO_INFORMADA') AS razao_social,
  p.registro_ans,
  p.total_primeiro,
  p.total_ultimo,
  ROUND(((p.total_ultimo - p.total_primeiro) / NULLIF(p.total_primeiro, 0)) * 100, 2) AS crescimento_percentual
FROM piv_q1 p
LEFT JOIN operadoras o ON o.registro_ans = p.registro_ans
WHERE p.total_primeiro > 0
ORDER BY crescimento_percentual DESC
LIMIT 5;


-- QUERY 2
WITH ultimos_3 AS (
  SELECT ano, trimestre
  FROM (
    SELECT DISTINCT ano, trimestre
    FROM despesas_consolidadas
    ORDER BY ano DESC, trimestre DESC
    LIMIT 3
  ) t
),
total_por_operadora AS (
  SELECT
    dc.cnpj AS registro_ans,
    SUM(dc.valor_despesas) AS total_3_trimestres
  FROM despesas_consolidadas dc
  JOIN ultimos_3 u
    ON u.ano = dc.ano AND u.trimestre = dc.trimestre
  GROUP BY dc.cnpj
),
operadora_uf AS (
  SELECT
    o.uf,
    t.registro_ans,
    t.total_3_trimestres
  FROM total_por_operadora t
  JOIN operadoras o ON o.registro_ans = t.registro_ans
)
SELECT
  uf,
  SUM(total_3_trimestres) AS total_despesas_uf,
  COUNT(DISTINCT registro_ans) AS qtd_operadoras,
  ROUND(SUM(total_3_trimestres) / NULLIF(COUNT(DISTINCT registro_ans), 0), 2) AS media_por_operadora_uf
FROM operadora_uf
WHERE uf IS NOT NULL AND uf <> ''
GROUP BY uf
ORDER BY total_despesas_uf DESC
LIMIT 5;


-- QUERY 3
WITH ultimos_3 AS (
  SELECT ano, trimestre
  FROM (
    SELECT DISTINCT ano, trimestre
    FROM despesas_consolidadas
    ORDER BY ano DESC, trimestre DESC
    LIMIT 3
  ) t
),
totais_por_operadora_trimestre AS (
  SELECT
    dc.cnpj AS registro_ans,
    dc.ano,
    dc.trimestre,
    SUM(dc.valor_despesas) AS total_trimestre
  FROM despesas_consolidadas dc
  JOIN ultimos_3 u
    ON u.ano = dc.ano AND u.trimestre = dc.trimestre
  GROUP BY dc.cnpj, dc.ano, dc.trimestre
),
media_geral_por_trimestre AS (
  SELECT
    ano,
    trimestre,
    AVG(total_trimestre) AS media_trimestre
  FROM totais_por_operadora_trimestre
  GROUP BY ano, trimestre
),
acima_da_media AS (
  SELECT
    t.registro_ans,
    COUNT(*) AS trimestres_acima
  FROM totais_por_operadora_trimestre t
  JOIN media_geral_por_trimestre m
    ON m.ano = t.ano AND m.trimestre = t.trimestre
  WHERE t.total_trimestre > m.media_trimestre
  GROUP BY t.registro_ans
)
SELECT
  COUNT(*) AS qtd_operadoras
FROM acima_da_media
WHERE trimestres_acima >= 2;
