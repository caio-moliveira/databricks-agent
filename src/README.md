# 🚀 Databricks RAG Chatbot: Guia de Implementação com Vector Search e LangChain

Este guia passo a passo detalha o processo de construção e deployment de um aplicativo **RAG (Retrieval-Augmented Generation)** usando **LangChain**, **Databricks Vector Search** e **Streamlit**, com deployment final na plataforma Databricks.

O projeto utiliza o catálogo Unity do Databricks para armazenar dados de produtos e o Vector Search para criar uma base de conhecimento semântica, permitindo que o LLM responda a perguntas complexas sobre o catálogo.

---

## 🗺️ Fluxo do Workshop

O projeto segue o seguinte fluxo de trabalho:

1.  **Criação do Vector Search Index** na tabela `produtos`.
2.  **Configuração das Variáveis de Ambiente** necessárias para a conexão.
3.  **Construção da Chain RAG** com LangChain (`main.py`).
4.  **Criação do Frontend** com Streamlit (`app.py`).
5.  **Deployment** do aplicativo no Databricks Compute > Apps.

---

## 1. Criação do Vector Search Index

Para habilitar a busca semântica em nosso catálogo de produtos, criaremos um Vector Search Index a partir da tabela `ai-agent-workshop.data.produtos`.

**Pré-condição:** As tabelas `clientes`, `produtos` e `vendas` já devem estar criadas no Unity Catalog.

### 📝 Passos no Databricks Workspace

1.  No seu Databricks Workspace, navegue até **Catalog**.
2.  Localize a tabela de produtos: `ai-agent-workshop.data.produtos`.
3.  Clique no botão **Create** no canto superior direito e selecione **Vector Search Index**.
4.  Configure o Index com os seguintes parâmetros:
    * **Source Table:** `ai-agent-workshop.data.produtos`
    * **Primary Key:** `id_produto`
    * **Columns to Sync (Sincronizar):** Marque as colunas que serão retornadas junto com a busca vetorial:
        * `nome_produto`
        * `categoria`
        * `preco`
        * `ativo`
    * **Column to be used for Embedding:** `descricao` (Esta coluna será usada para gerar os vetores).
    * **Embedding Model:** `databricks-gte-large-en`
    * **Vector Search Endpoint:** `my-vector-search` (Certifique-se de que este endpoint esteja ativo. Ele será referenciado no seu código como `VS_ENDPOINT`).
5.  Clique em **Create**.

Aguarde o status do Index mudar para `READY`. Este será o seu `INDEX_NAME`.

---

## 2. Configuração das Variáveis de Ambiente

O aplicativo requer diversas variáveis de ambiente para conectar-se aos serviços do Databricks (Vector Search, LLM Endpoint, MLflow) e, opcionalmente, a serviços externos (OpenAI).

Crie um arquivo `.env` ou configure estas variáveis diretamente no ambiente de deployment com os seus respectivos valores.

| Variável | Descrição | Exemplo de Valor |
| :--- | :--- | :--- |
| `VS_ENDPOINT` | Nome do seu Endpoint de Vector Search (Criado no Passo 1). | `"my-vector-search"` |
| `INDEX_NAME` | Path completo do Vector Search Index (Catálogo.Schema.Index). | `"ai-agent-workshop.data.produtos_index"` |
| `LLM_ENDPOINT` | Endpoint de Serving do LLM a ser usado. | `"databricks-meta-llama-3-3-70b-instruct"` |
| `MODEL_NAME` | Nome para o trace do MLflow. | `"nome-do-trace"` |
| `EXPERIMENT_ID` | ID do Experimento MLflow para rastrear as corridas. | `"seu-id-experimento"` |
| `MLFLOW_TRACKING_URI` | URI para rastreamento do MLflow (geralmente `"databricks"`). | `"databricks"` |
| `DATABRICKS_HOST` | URL do seu Workspace Databricks. | `"https://seu-id.cloud.databricks.com"` |
| `DATABRICKS_TOKEN` | Token de Acesso Pessoal para autenticação. | `"seu-token"` |
| `DATABRICKS_ACCOUNT_ID` | ID da sua conta Databricks (opcional, dependendo do uso). | `"seu-id-conta"` |
| `OPENAI_API_KEY` | Chave API da OpenAI (necessária se usar modelos da OpenAI). | `'sua-chave-api-openai'` |

> **Nota:** As variáveis `DATABRICKS_HOST` e `DATABRICKS_TOKEN` são essenciais para a autenticação no ambiente de deployment, especialmente via Compute Apps.

---

## 3. Construção do Código (LangChain e Streamlit)

### 3.1. **Cadeia RAG Principal (`main.py`)**

O arquivo `main.py` contém a lógica central do RAG, orquestrada com LangChain.

* **Função:** `get_rag_chain()`
* **O que faz:**
    1.  **Retriever:** Inicializa o `DatabricksVectorSearch` usando `VS_ENDPOINT` e `INDEX_NAME` para buscar os documentos de produtos mais relevantes com base na consulta do usuário.
    2.  **Prompt Template:** Define a instrução (System Prompt) para o LLM, orientando-o a atuar como um **"assistente de recomendação de produtos"** e a usar o contexto recuperado para formatar a resposta.
    3.  **LLM:** Inicializa o `ChatDatabricks` utilizando o `LLM_ENDPOINT` configurado.
    4.  **Chain (LCEL):** Conecta o Retriever, o Prompt e o LLM usando a LangChain Expression Language (`RunnableMap | prompt | llm | StrOutputParser()`), garantindo um fluxo de dados eficiente.

### 3.2. **Interface do Usuário (`app.py`)**

O arquivo `app.py` constrói a interface gráfica usando o Streamlit.

* **Função:** Criar o frontend para interação do usuário com o Chatbot RAG.
* **O que faz:**
    1.  **Inicialização:** Usa `@st.cache_resource` para inicializar a chain LangChain **apenas uma vez** (via `get_rag_chain()`).
    2.  **Histórico de Chat:** Gerencia as mensagens anteriores usando `st.session_state`.
    3.  **Processamento da Entrada:** Captura a pergunta do usuário (`st.chat_input`).
    4.  **Invocação e MLflow:** Inicia um novo **MLflow Run** (`mlflow.start_run`) para cada consulta, invoca a `chain.invoke()` com a pergunta e registra os parâmetros de entrada e a resposta, facilitando o rastreamento e a depuração.
    5.  **Exibição:** Exibe o histórico de mensagens e a resposta do assistente no formato de chat.

---

## 4. Deployment no Databricks

Após configurar os arquivos e variáveis, o aplicativo Streamlit pode ser implantado como um **Databricks App**.

**Pré-requisito:** Certifique-se de que você tem um arquivo de configuração como o `app.yaml` que define o comando de execução e as variáveis de ambiente a serem passadas.

### 📝 Passos para o Deploy

1.  **Pacote de Deployment:** Certifique-se de que todos os arquivos necessários (`main.py`, `app.py`, `settings.py`, `requirements.txt`, `app.yaml`) estão prontos para serem empacotados e acessados (ex: em um repositório Git ou DBFS).
2.  **Navegue para Apps:** No seu Databricks Workspace, navegue até a seção **Compute** (Computação).
3.  Selecione a aba **Apps**.
4.  Clique em **Create App**.
5.  Configure os detalhes do App:
    * **Source:** Selecione a fonte do seu código (ex: Databricks Repos, que é altamente recomendado).
    * **App Name:** Dê um nome ao seu aplicativo (ex: `rag-produtos-streamlit`).
    * **YAML File Path:** Indique o caminho para o seu arquivo de configuração de deployment (ex: `app.yaml`).
    * **Cluster/Compute Config:** Selecione ou configure o tipo de recurso de computação onde o app será executado.
    * **Environment Variables:** Adicione as variáveis de ambiente listadas no **Passo 2** na seção de configurações.
6.  Clique em **Create** e monitore o status do seu aplicativo.

Uma vez que o App estiver em status `READY` (Pronto), você poderá acessar o link para interagir com o seu Chatbot RAG de Produtos.