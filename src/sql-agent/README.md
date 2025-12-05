# 🤖 Databricks SQL Agent: Análise Financeira com LangChain

Este projeto apresenta um **Agente de Linguagem Natural para SQL** (**Text-to-SQL Agent**) que se conecta a um **Databricks SQL Warehouse** utilizando o framework **LangChain**. Ele permite que usuários façam perguntas em **Português** sobre dados financeiros, e o agente as traduz para consultas SQL, executa a consulta no Databricks e retorna a resposta de forma compreensível.

A solução utiliza o **SQLAlchemy** para estabelecer a conexão robusta e o modelo **LLM** (Large Language Model) para orquestrar o raciocínio.

## 🗺️ Fluxo de Implementação

1.  **Criação da View Analítica:** Combinar as tabelas existentes (`clientes`, `produtos`, `vendas`) em uma única View para facilitar a consulta pelo Agente.
2.  **Configuração da Conexão:** Obter as variáveis de ambiente necessárias para conectar o Agente ao **Databricks SQL Warehouse**.
3.  **Desenvolvimento do Agente:** Usar LangChain para criar o `SQLDatabaseToolkit` e o Agente.
4.  **Deployment:** Implementação final para uso.

-----

## 1\. Preparação dos Dados: Criação da View Analítica

Para que o Agente SQL possa responder a perguntas que envolvem diferentes entidades (quem comprou o quê, quando), é crucial consolidar os dados das três tabelas (`clientes`, `produtos`, `vendas`) em uma única **View**.

### 1.1. 💾 Script SQL (Exemplo)

Execute o seguinte comando SQL no seu Databricks SQL Editor. O nome da View será `financas_vendas`, no catálogo e schema já existentes (`ai-agent-workshop.data`).

```sql
-- Garante que a VIEW existe para o Agente SQL
CREATE OR REPLACE VIEW `ai-agent-workshop`.data.financas_vendas AS
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
  p.preco           AS preco_unitario,
  p.ativo           AS produto_ativo,
  
  -- Vendas
  v.quantidade,
  v.preco_unitario_venda,
  v.quantidade * v.preco_unitario_venda AS valor_total_venda
  
FROM `ai-agent-workshop`.data.vendas AS v
INNER JOIN `ai-agent-workshop`.data.clientes AS c ON v.id_cliente = c.id_cliente
INNER JOIN `ai-agent-workshop`.data.produtos AS p ON v.id_produto = p.id_produto;
```

**Permissão:** Certifique-se de que o usuário/entidade de serviço que executará o Agente tenha a permissão **`SELECT`** na View `ai-agent-workshop.data.financas_vendas`.

-----

## 2\. Configuração da Conexão e Variáveis de Ambiente

O Agente SQL requer detalhes de conexão para acessar o Databricks SQL Warehouse. Essas variáveis são usadas no arquivo **`db.py`** para construir a string de conexão SQLAlchemy.

| Variável | Descrição | Exemplo de Valor |
| :--- | :--- | :--- |
| `DATABRICKS_SERVER_HOSTNAME` | Hostname do seu Workspace. | `"seu-id.cloud.databricks.com"` |
| `DATABRICKS_HTTP_PATH` | HTTP Path do seu SQL Warehouse (encontrado em Compute \> SQL Warehouses). | `"/sql/1.0/warehouses/id-do-warehouse"` |
| `DATABRICKS_TOKEN` | Token de Acesso Pessoal (PAT) com permissão para acessar o Warehouse e o Unity Catalog. | `"seu-token"` |
| `OPENAI_API_KEY` | (Opcional) Chave API da OpenAI, se estiver usando um LLM externo. | `'sua-chave-api-openai'` |

> **Observação:** O arquivo `db.py` (código fornecido) usa essas variáveis para criar um `engine` que será a base do `SQLDatabaseToolkit` da LangChain.

-----

## 3\. Desenvolvimento do Agente SQL (`databricks-agent.py`)

O Agente utiliza o `SQLDatabaseToolkit` da LangChain para ter acesso a ferramentas como `list_tables`, `schema_for_table` e `query_sql`, que são as ações que ele pode realizar no banco de dados.

### 3.1. Visão Geral do `databricks-agent.py`

O Agente é configurado com os seguintes componentes:

1.  **Conexão (SQLDatabase):**

      * Inicializa a conexão (`db`) com o Databricks usando o `engine` de `db.py`.
      * Apenas a View analítica (`financas_vendas`) é incluída, limitando o escopo de dados do Agente.

    <!-- end list -->

    ```python
    # db.py provê o 'engine'
    from .db import engine
    # ...
    db = SQLDatabase(
        engine,
        include_tables=["financas_vendas"], # Apenas a View que criamos
    )
    ```

2.  **Toolkit e LLM:**

      * O `SQLDatabaseToolkit` é criado, dando ao LLM acesso às operações SQL.
      * Um **LLM** (ex: `ChatOpenAI` ou `ChatDatabricks`) é definido para raciocínio.

3.  **Criação do Agente:**

      * A função `create_sql_agent` da LangChain é usada para montar o agente, definindo o `agent_type` (ex: `"openai-tools"`) e o **System Prompt**.

    <!-- end list -->

    ```python
    # databricks-agent.py
    # ...
    SYSTEM_PROMPT_PT = """
    Você é um analista de dados que responde em português, gerando apenas SQL compatível com Databricks SQL
    quando precisar consultar dados.
    Traga a resposta sempre no formato de texto, não em tabelas.
    """

    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        agent_type="openai-tools", 
        verbose=True, # Importante para ver os passos de raciocínio
        system_message=SYSTEM_PROMPT_PT,
        top_k=5, 
    )
    # ...
    ```

### 3.2. Raciocínio do Agente

Quando o `verbose=True`, o Agente exibirá seu processo de raciocínio (Thought/Action/Observation):

1.  **Thought (Pensamento):** "Preciso saber quais colunas estão disponíveis na tabela `financas_vendas`."
2.  **Action (Ação):** `sql_db_schema` (Tool) com input `financas_vendas`.
3.  **Observation (Observação):** Recebe o schema da View.
4.  **Thought (Pensamento):** "Agora, com base na pergunta, vou gerar o SQL para contar as vendas por mês."
5.  **Action (Ação):** `sql_db_query` (Tool) com o input do SQL gerado.
6.  **Observation (Observação):** Recebe o resultado da consulta do Databricks.
7.  **Thought (Pensamento):** "Vou traduzir o resultado para um texto em português."
8.  **Final Answer (Resposta Final):** Retorna a resposta para o usuário.

-----

## 4\. Deployment e Execução

O Agente pode ser executado dentro de notebooks Databricks ou, como no projeto anterior, integrado a um aplicativo Streamlit ou FastAPI para deployment via **Databricks Compute \> Apps**.

Para executar, basta importar a função `ask` do seu arquivo `databricks-agent.py`:

```python
# Exemplo de Execução
from databricks_agent import ask

pergunta = "Qual a categoria de produto com maior valor total de vendas no último trimestre?"

resposta = ask(pergunta)
print(resposta)
```

O agente agora está pronto para responder a perguntas complexas de forma conversacional, traduzindo-as em consultas estruturadas no Databricks.

