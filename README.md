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

-----


## 🎯 **Sobre o Workshop**

Este repositório faz parte do conteúdo prático do **Workshop Databricks** da **Jornada de Dados**, onde desenvolvemos um projeto completo de **Agentes de IA corporativos** com foco em integração entre **Databricks + LangChain**.

O objetivo é mostrar, passo a passo, como construir uma solução moderna de Inteligência Artificial que combina:

  * **Vector Search** para buscas semânticas.
  * **LLMs** hospedados nativamente no Databricks.
  * **LangChain** para orquestrar a arquitetura RAG.
  * **MLflow** para rastreamento e observabilidade.
  * **Streamlit** como interface amigável para o usuário final.

-----

## 🤖 **O que você vai construir**

Durante este módulo, você desenvolverá um **Chatbot Financeiro Inteligente**, capaz de:

  * Consultar dados estruturados e semiestruturados.
  * Responder perguntas de negócio em linguagem natural.
  * Interpretar registros de vendas, clientes e produtos.
  * Utilizar Vector Search para respostas baseadas em similaridade.
  * Registrar toda a execução da pipeline no MLflow.
  * Expor a solução em um frontend interativo com Streamlit.

Esse é um **projeto completo**, replicável e pronto para uso em ambientes reais de negócio.

-----

## 🚀 Fase 0: Configuração Inicial do Ambiente

Esta fase inicial garante que seu ambiente Databricks esteja pronto com os dados e estruturas necessárias (Catalog, Schema e Tabelas) para o workshop.

### 1\. Clonagem do Repositório

Comece clonando este repositório para o seu Databricks Repos ou máquina local:

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd <nome-do-repositorio>
```

### 2\. Configuração do Unity Catalog

Para padronizar o ambiente, utilizaremos um **Catalog** e um **Schema** específicos.

1.  **Crie o Catalog:**
      * Navegue até o **Catalog Explorer** no seu Workspace Databricks.
      * Clique em **Create Catalog** e nomeie-o como: `ai-agent-workshop`
2.  **Crie o Schema (dentro do Catalog):**
      * Dentro do Catalog `ai-agent-workshop`, clique em **Create Schema** e nomeie-o como: `data`

O caminho final para suas tabelas será: `ai-agent-workshop.data.<tabela>`

### 3\. Upload dos Arquivos para Volume

Vamos usar a funcionalidade de **Volumes** do Unity Catalog para hospedar os arquivos brutos (`.csv`) antes de criar as tabelas Delta.

1.  **Crie ou Navegue até um Volume:**
      * No Catalog Explorer, dentro do seu Catalog (`ai-agent-workshop`) e Schema (`data`), navegue até a aba **Volumes**.
      * Crie um novo Volume (ex: `data`). O caminho final será: `/Volumes/ai-agent-workshop/data/data`.
2.  **Upload dos Arquivos:**
      * Os arquivos de dados estão na pasta `data/` do repositório (`clientes.csv`, `produtos.csv`, `vendas.csv`).
      * Faça o upload desses **três arquivos** diretamente para o Volume que você acabou de criar (`/Volumes/ai-agent-workshop/data/data`).

### 4\. Criação das Tabelas Iniciais (Delta Tables)

Crie um **novo Notebook** no Databricks, anexe-o a um **Cluster** (Databricks Runtime 13.3 LTS+ é recomendado) e execute os comandos abaixo, que leem os CSVs do Volume e criam as tabelas Delta no Unity Catalog.

> **Ajuste o caminho:** Certifique-se de que o caminho do `LOCATION` esteja apontando corretamente para o Volume onde você subiu os arquivos (ex: `'/Volumes/ai-agent-workshop/data/data/'`).

```sql
-- Garante que estamos usando o schema correto
USE CATALOG `ai-agent-workshop`;
USE SCHEMA data;
```

```py
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

```py
df_clientes.write.mode("overwrite").saveAsTable("`ai-agent-workshop`.data.clientes")

df_produtos.write.mode("overwrite").saveAsTable("`ai-agent-workshop`.data.produtos")

df_vendas.write.mode("overwrite").saveAsTable("`ai-agent-workshop`.data.vendas")
```

Ao final desta etapa, você terá as seguintes tabelas **Delta** disponíveis no seu Unity Catalog:

  * `ai-agent-workshop.data.clientes`
  * `ai-agent-workshop.data.produtos`
  * `ai-agent-workshop.data.vendas`

-----

## ➡️ Próximos Passos

Agora que os dados estão prontos, o workshop se divide em dois projetos principais:

1.  **[Projeto 1: Agente RAG (Vector Search)](https://github.com/caio-moliveira/databricks-agent/blob/main/src/README.md)** (utiliza a tabela `produtos`)
2.  **[Projeto 2: Agente SQL (Text-to-SQL)](https://github.com/caio-moliveira/databricks-agent/blob/main/src/sql-agent/README.md)** (utiliza as tabelas `clientes`, `produtos`, `vendas`)

**Utilizando LLM models do Databricks [Exemplo utilizando Models-Serving)](https://github.com/caio-moliveira/databricks-agent/blob/main/src/example/README.md).**

