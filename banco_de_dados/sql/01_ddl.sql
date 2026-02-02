DROP TABLE IF EXISTS despesas_consolidadas;
DROP TABLE IF EXISTS despesas_agregadas;
DROP TABLE IF EXISTS operadoras;

CREATE TABLE operadoras (
  cnpj              VARCHAR(14) PRIMARY KEY,
  razao_social      TEXT NOT NULL,
  registro_ans      VARCHAR(20),
  modalidade        TEXT,
  uf                CHAR(2)
);

CREATE INDEX idx_operadoras_uf ON operadoras(uf);

CREATE TABLE despesas_consolidadas (
  id                BIGSERIAL PRIMARY KEY,
  cnpj              VARCHAR(14) NOT NULL,
  razao_social      TEXT NOT NULL,
  ano               SMALLINT NOT NULL,
  trimestre         SMALLINT NOT NULL,
  valor_despesas    NUMERIC(18,2) NOT NULL,
  CONSTRAINT fk_consolidadas_operadoras
    FOREIGN KEY (cnpj) REFERENCES operadoras(cnpj)
);

CREATE INDEX idx_consolidadas_cnpj ON despesas_consolidadas(cnpj);
CREATE INDEX idx_consolidadas_ano_tri ON despesas_consolidadas(ano, trimestre);

CREATE TABLE despesas_agregadas (
  id                BIGSERIAL PRIMARY KEY,
  razao_social      TEXT NOT NULL,
  uf                CHAR(2) NOT NULL,
  total_despesas    NUMERIC(18,2) NOT NULL,
  media_trimestral  NUMERIC(18,2),
  desvio_padrao     NUMERIC(18,2)
);

CREATE INDEX idx_agregadas_uf ON despesas_agregadas(uf);
CREATE INDEX idx_agregadas_total ON despesas_agregadas(total_despesas);
