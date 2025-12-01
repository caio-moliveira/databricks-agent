Aqui está uma **versão revisada, mais clara, mais atrativa e mais organizada** da sua introdução — mantendo **todas as imagens, badges, links e estrutura**, mas elevando o texto para um nível mais profissional e convidativo:

---

<div align="center">
  <img src="./assets/jornada.png" alt="Jornada de Dados" width="200"/>

# **Workshop: Databricks – Construindo Agentes de IA**

### [Jornada de Dados](https://suajornadadedados.com.br/)

**Workshop prático sobre criação de agentes de IA no Databricks, integrando LangChain e Vector Search**

[![Workshop](https://img.shields.io/badge/Workshop-Agentes%20de%20IA-blue?style=for-the-badge)](https://jornadadedados.alpaclass.com/c/cursos/jAZX23)
[![Databricks](https://img.shields.io/badge/Databricks-Lakehouse-orange?style=for-the-badge&logo=databricks)](https://www.databricks.com/)
[![LangChain](https://img.shields.io/badge/LangChain-Framework-blueviolet?style=for-the-badge&logo=chainlink)](https://docs.langchain.com/)
[![Python](https://img.shields.io/badge/Python-3.12+-green?style=for-the-badge\&logo=python)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-lightgrey?style=for-the-badge\&logo=openai)](https://openai.com/)

</div>


## 🎯 **Sobre o Workshop**

Este repositório faz parte do conteúdo prático do **Workshop Databricks** da **Jornada de Dados**, onde desenvolvemos um projeto completo de **Agentes de IA corporativos** com foco em integração entre **Databricks + LangChain**.

O objetivo é mostrar, passo a passo, como construir uma solução moderna de Inteligência Artificial que combina:

* Vector Search para buscas semânticas
* LLMs hospedados nativamente no Databricks
* LangChain para orquestrar a arquitetura RAG
* MLflow para rastreamento e observabilidade
* Streamlit como interface amigável para o usuário final

---

## 🤖 **O que você vai construir**

Durante este módulo, você desenvolverá um **Chatbot Financeiro Inteligente**, capaz de:

* Consultar dados estruturados e semiestruturados
* Responder perguntas de negócio em linguagem natural
* Interpretar registros de vendas, clientes e produtos
* Utilizar Vector Search para respostas baseadas em similaridade
* Registrar toda a execução da pipeline no MLflow
* Expor a solução em um frontend interativo com Streamlit

Esse é um **projeto completo**, replicável e pronto para uso em ambientes reais de negócio.

---

# 📁 Estrutura Geral do Projeto

```
project/
│
├── data/
│   ├── clientes.csv
│   ├── produtos.csv
│   └── vendas.csv
├── src/
│   ├── app.py
│   ├── main.py
│   ├── settings.py
└── README.md
```

---

# 🧱 1. Criando o Catalog, Schema e Volume

No Databricks:

1. **Catalog:** `ai-agent-workshop`
2. **Schema:** `data`
3. **Volume:** crie um volume dentro do schema (Eu chamei o meu de 'data')
4. Faça upload dos arquivos CSV dentro de:

```
ai-agent-workshop / data / <seu-volume>
```

---

# 🔥 2. Criando as Tabelas do Projeto

Abra um **notebook** e execute:

```sql
USE CATALOG `ai-agent-workshop`;
```

### **Carregando CSVs**

```python
# Ajuste os paths conforme o nome do volume criado no Databricks
path_clientes = "dbfs:/Volumes/ai-agent-workshop/data/data/clientes.csv"
path_produtos = "dbfs:/Volumes/ai-agent-workshop/data/data/produtos.csv"
path_vendas   = "dbfs:/Volumes/ai-agent-workshop/data/data/vendas.csv"

df_clientes = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(path_clientes)
)

df_produtos = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(path_produtos)
)

df_vendas = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(path_vendas)
)
```

### **Criando as Tabelas Delta**

```python
df_clientes.write.mode("overwrite").saveAsTable("`ai-agent-workshop`.data.clientes")
df_produtos.write.mode("overwrite").saveAsTable("`ai-agent-workshop`.data.produtos")
df_vendas.write.mode("overwrite").saveAsTable("`ai-agent-workshop`.data.vendas")
```

---

# 📊 3. Criando a View Analítica

```sql
CREATE OR REPLACE VIEW `ai-agent-workshop`.data.vw_financas_vendas AS
SELECT
  v.id_venda,
  v.data_venda,
  DATE(v.data_venda)                AS data,
  YEAR(v.data_venda)                AS ano,
  MONTH(v.data_venda)               AS mes,

  -- Cliente
  v.id_cliente,
  c.nome_cliente,
  c.segmento        AS segmento_cliente,
  c.cidade          AS cidade_cliente,
  c.estado          AS estado_cliente,

  -- Produto
  v.id_produto,
  p.nome_produto,
  p.categoria       AS categoria_produto,

  -- Métricas da venda
  v.quantidade,
  v.valor_unitario,
  v.valor_total     AS receita_venda,
  v.canal_venda

FROM `ai-agent-workshop`.data.vendas   AS v
JOIN `ai-agent-workshop`.data.clientes AS c
  ON v.id_cliente = c.id_cliente
JOIN `ai-agent-workshop`.data.produtos AS p
  ON v.id_produto = p.id_produto;
```

---

# 🧬 4. Tabela Semântica para RAG

```sql
CREATE OR REPLACE TABLE `ai-agent-workshop`.data.financas_semantica AS
SELECT
  CAST(id_venda AS STRING)                  AS id_registro,
  'venda'                                   AS tipo,
  CONCAT(
    'Venda ', CAST(id_venda AS STRING),
    ' realizada em ', CAST(data AS STRING),
    ' para o cliente ', nome_cliente,
    ' (segmento ', segmento_cliente, ', cidade ', cidade_cliente, ' - ', estado_cliente, '). ',
    'Produto: ', nome_produto, ' (categoria ', categoria_produto, '). ',
    'Quantidade: ', CAST(quantidade AS STRING),
    ', valor unitário R$', CAST(valor_unitario AS STRING),
    ', valor total R$', CAST(receita_venda AS STRING),
    '. Canal de venda: ', canal_venda, '.'
  ) AS texto_busca,

  -- Metadados adicionais úteis
  data,
  ano,
  mes,
  nome_cliente,
  segmento_cliente,
  cidade_cliente,
  estado_cliente,
  nome_produto,
  categoria_produto,
  quantidade,
  valor_unitario,
  receita_venda,
  canal_venda
FROM `ai-agent-workshop`.data.vw_financas_vendas;
```

---

# 🧭 5. Criando a Tabela Vetorial

Navegue no Databricks:

1. **Compute → Vector Search**
2. Clique em **Create Endpoint**
3. Nome: `my-vector-search`
4. Associe à tabela:

```
ai-agent-workshop.data.financas_semantica
```

5. Crie o índice:

```
ai-agent-workshop.data.financas_semantica_index
```


---

# ▶️ 6. Instalação & Execução

> Pré-requisitos: **Python 3.13+** e **uv** instalado (`pip install uv` ou veja a doc do uv).

### 1) Clonar o repositório

```bash
git clone https://github.com/<seu-usuario>/<seu-repo>.git
cd <seu-repo>
```

### 2) Criar e ativar o ambiente com `uv`

```bash
# (Opcional) garantir Python 3.12 disponível pelo uv
uv python install 3.13

# criar venv
uv venv
```

**Ativar o ambiente:**

* **Windows (PowerShell):**

```powershell
. .venv\Scripts\Activate
```

* **macOS / Linux:**

```bash
source .venv/bin/activate
```

### 3) Instalar dependências do `pyproject.toml`

```bash
uv sync
```

> O `uv sync` instala tudo que está no `pyproject.toml` (e `uv.lock`, se existir), sem precisar de `requirements.txt`.

### 4) Configurar variáveis de ambiente (`.env`)

Crie um arquivo `.env` na raiz do projeto com as variáveis abaixo (ajuste os valores):

```env
# === Credenciais & Acesso ===
OPENAI_API_KEY=sk-xxxxxx                                # se usar OpenAI (opcional conforme seu LLM)
DATABRICKS_HOST=https://<seu-workspace>.cloud.databricks.com
DATABRICKS_TOKEN=dapi-xxxxxxxxxxxxxxxxxxxxxxxx

# === MLflow ===
MLFLOW_TRACKING_URI=databricks                          # mantém "databricks"
EXPERIMENT_ID=1234567890                                # ID do experimento no Databricks

# === Vector Search ===
VS_ENDPOINT=my-vector-search                            # nome do endpoint criado em Compute > Vector Search
VS_INDEX=ai-agent-workshop.data.financas_semantica_index

# === LLM no Databricks ===
LLM_EP=databricks-meta-llama-3-3-70b-instruct           # endpoint de modelo (ajuste para o seu)
MODEL_NAME=langchain_rag_demo                           # identificador lógico interno (livre)

# === (Opcional) Conta/Workspace ===
DATABRICKS_ACCOUNT_ID=                                  # use se necessário em sua org
```

> O projeto já carrega essas variáveis via `dotenv` no `settings.py`.

### 5) Executar o app (Streamlit)

```bash
streamlit run app.py
```

Acesse: `http://localhost:8501`

---
