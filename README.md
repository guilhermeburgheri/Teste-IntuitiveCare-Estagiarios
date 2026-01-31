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

### 2.1 - Validação de dados com diferentes estratégias [FEITO]
- Validando os dados conforme necessidade:
  - Valor das despesas: Deve ser numérico e positivo.
  - Razão social: não pode estar vazia.
  - CNPJ: Calculo para verificar se é válido.

### 2.2 - Enriquecendo dados e tratando falahas [FEITO]
- O cadastro foi retirado pela API também disponibilizada pela ANS: https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/
- Ficando o RegistroANS como identificador primário e CNPJ para cadastro.
- Campos criados:
  - CNPJ
  - RazaoSocial
  - UF
  - Modalidade 

- Trade-off técnico: Optei por carregar de forma completa por não possuir uma grande quantidade de arquivos e facilitar as joins.

### 2.3 - Agregando os dados [FEITO]
- Agregando as despesas de acordo com a Razão Social e UF.
- Possui o total da despesa junto com a média e o desvio de acordo com os trimestres.

- Trade-off técnico: Optei por ordenar depois de agregar os dados por que assim o tamanho do arquivo está bem menor, tornando o processo mais rápido.


### Tratamento de inconsistências e falhas
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

- CNPJ inválidos ainda são mantidos em um outro arquivo para evitar perda de dados que possam ser importantes em algum momento.

- RegistroANS duplicados serão mantidos apenas os primeiros para não causar conflito nas informações.
- RegistroANS inválidos ainda são mantidos em um outro arquivo para evitar perda de dados que possam ser importantes em algum momento.
    
---

## Decisões técnicas

### Uso de bibliotecas
- A biblioteca **Pandas** não foi utilizada devido às políticas de segurança do sistema. Para evitar alterações nas configurações do Windows, o projeto foi desenvolvido apenas com bibliotecas nativas do Python.

---

## Execução do processo

- Os comandos devem ser executados na pasta raiz do projeto, segue a ordem:
  - py -m ans_dados.cli
  - py -m ans_dados.enriquece_dados
  - py -m ans_dados.valida_dados
  - py -m ans_dados.agrega_dados

--- 

## Estrutura do projeto
```
ans_dados/
├── agrega_dados.py
├── ans_source.py
├── cli.py
├── consolida_dados.py
├── enriquece_dados.py
├── processa_dados.py
└── valida_dados.py
```
