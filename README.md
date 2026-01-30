# Integração com Dados Abertos da ANS

Projeto desenvolvido em Python para integração com a API pública de Dados Abertos da ANS.  
O objetivo é realizar o download, processamento e gerar um novo arquivo já formatado e filtrado dos últimos 3 trimestres disponíveis.

## Etapas do desafio

### 1.1 – Integração com API [FEITO]
- Identificação automática dos últimos 3 trimestres disponíveis.
- Download dos arquivos .zip a partir da API da ANS.

### 1.2 – Processamento de arquivos [FEITO]
- Extração automática dos arquivos .zip.
- Leitura de arquivos nos formatos CSV, TXT e XLSX.
- Trade-off técnico: Optei por processar incrementalmente para reduzir uso de memória e evitar problemas com a grande quantidade de arquivos.

Nesta etapa, o arquivo é considerado válido caso contenha ao menos uma ocorrência relacionada a Eventos/Sinistros em qualquer uma de suas linhas.

### 1.3 – Filtrando e coletando inconsistências [FEITO]
- Consolidação dos dados dos 3 trimestres em um único arquivo CSV.
- Normalização das colunas para o formato:
  - CNPJ
  - Razao Social
  - Trimestre
  - Ano
  - Valor Despesas
- Geração do arquivo consolidado.csv.
- Compactação do resultado final em consolidado_despesas.zip.

### Tratamento de inconsistências
Durante o processo, as seguintes inconsistências foram identificadas, registradas em um arquivo separado e tratadas:

- *CNPJ duplicado com razão social diferente*  
  - A primeira razão social encontrada é mantida.
  - A ocorrência é registrada como inconsistência.

- *Valores zerados ou negativos*  
  - Os valores são mantidos na soma.
  - A ocorrência é registrada como inconsistência.

- *Trimestre ou ano não identificável*  
  - O arquivo é ignorado.
  - A ocorrência é registrada como inconsistência.
    
---

## Decisões técnicas

### Uso de bibliotecas
- A biblioteca **Pandas** não foi utilizada devido às políticas de segurança do sistema. Para evitar alterações nas configurações do Windows, o projeto foi desenvolvido apenas com bibliotecas nativas do Python.

---

## Estrutura do projeto
```
ans_dados/
├── ans_source.py
├── processa_dados.py
├── consolida_dados.py
└── cli.py
```
