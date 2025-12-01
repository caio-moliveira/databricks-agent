# main.py
import os
import mlflow
from databricks_langchain import DatabricksVectorSearch, ChatDatabricks
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableMap
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from settings import settings


def ensure_query(d: dict) -> str:
    """Extrai a query da entrada do dicionário."""
    return d.get("messages", "") or d.get("query", "")


def format_ctx(docs):
    """Formata os documentos recuperados para serem inseridos no prompt."""
    return (
        ""
        if not docs
        else "\n\n---\n\n".join(getattr(x, "page_content", str(x)) for x in docs)
    )


def get_rag_chain():
    """
    Inicializa e retorna a chain RAG completa (Retriever, Prompt, LLM).
    """

    # 1. Retriever
    retriever = DatabricksVectorSearch(
        endpoint=settings.VS_ENDPOINT,
        index_name=settings.INDEX_NAME,
        columns=[
            "id_registro",
            "tipo",
            "ano",
            "mes",
            "nome_cliente",
            "segmento_cliente",
            "cidade_cliente",
            "estado_cliente",
            "nome_produto",
            "categoria_produto",
            "quantidade",
            "valor_unitario",
            "receita_venda",
            "canal_venda",
        ],
    ).as_retriever(
        search_kwargs={
            "k": 10,
            "query_type": "HYBRID",
        }
    )

    # 2. Promtp Template
    prompt = PromptTemplate.from_template(
        """
Você é um analista financeiro que responde perguntas sobre vendas, produtos e clientes
com base nos dados de uma empresa.

Você recebe como CONTEXTO uma lista de registros de vendas. Cada registro descreve:
- data da venda
- cliente (nome, segmento, cidade, estado)
- produto (nome, categoria)
- quantidade
- valor unitário
- valor total (receita_venda)
- canal de venda

INSTRUÇÕES:
- Use SOMENTE as informações do contexto para responder.
- Quando a pergunta envolver "produtos que mais venderam",
  "categorias que mais venderam", "clientes que mais compraram",
  "valor gasto total por cliente" ou similares:
    - Observe os registros do contexto e explique os padrões
      (por exemplo: produtos/cliente/categorias que se repetem, maior valor total, etc.).
- Se o contexto for limitado e não permitir resposta exata,
  deixe isso claro e diga que a resposta é baseada apenas no que foi retornado.
- Sempre responda em PORTUGUÊS, de forma clara, organizada e objetiva.
- Se não houver informação suficiente no contexto, diga isso explicitamente.

Pergunta do usuário:
{query}

Contexto:
{context}

Resposta:
"""
    )

    # 3. LLM
    llm = ChatDatabricks(endpoint=settings.LLM_ENDPOINT)

    # 4. Cadeia (Chain) do LangChain
    chain = (
        RunnableMap(
            {
                "query": RunnableLambda(ensure_query),
                "context": RunnableLambda(ensure_query)
                | retriever
                | RunnableLambda(format_ctx),
            }
        )
        | prompt
        | llm
        | StrOutputParser()
    )

    # Opcional: Configuração de MLflow (pode ser movida para o app.py ou mantida aqui)
    mlflow.set_tracking_uri("databricks")
    mlflow.set_experiment(experiment_id=settings.EXPERIMENT_ID)
    mlflow.langchain.autolog()

    return chain
