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
        columns=["nome_produto", "descricao", "categoria", "preco", "ativo"],
    ).as_retriever(
        search_kwargs={
            "k": 3,
            "query_type": "HYBRID",
        }
    )

    # 2. Promtp Template
    prompt = PromptTemplate.from_template("""
    Você é um **assistente de recomendação de produtos**.
    Sua tarefa é analisar o CONTEXTO (registros de produtos) e responder à PERGUNTA DO USUÁRIO
    **apenas** com base nesses registros.

    Cada item do CONTEXTO contém:
    - nome_produto
    - descricao
    - categoria
    - preco
    - ativo (booleano)

    REGRAS IMPORTANTES
    1) **Não use conhecimento externo.**
    2) Priorize produtos onde `ativo` == true.  
    - Se houver poucos itens ativos, preencha com inativos e explique isso em "observacoes".
    3) O foco de seleção é **aderência semântica** entre a consulta do usuário ({query}) e a coluna **descricao**.
    4) Explique sucintamente **por que** cada produto foi escolhido, citando características da coluna `descricao` que se relacionam com a busca.
    5) Sempre responda em **PORTUGUÊS**, de forma clara e objetiva.
    6) Saída obrigatória em **JSON**, SEM texto fora do JSON.

    COMO PRIORIZAR
    - Termos semelhantes entre a busca e a `descricao`.
    - Categoria mais compatível.
    - Produtos ativos primeiro.
    - Se houver empate, prefira:  
    (a) descrição mais específica,  
    (b) categoria mais alinhada,  
    (c) preço mais coerente com a intenção do usuário (se mencionada).

    FORMATO DE SAÍDA (JSON)
    {{
    "consulta_usuario": "<copie a consulta do usuário>",
    "itens": [
        {{
        "nome_produto": "<string>",
        "categoria": "<string>",
        "preco": <number>,
        "ativo": <true|false>,
        "score_aderencia": <number>,
        "justificativa": "<1 a 2 frases explicando o match com a descricao>"
        }}
    ],
    "observacoes": "<opcional: ex. 'faltaram produtos ativos', 'contexto limitado', etc>"
    }}

    PERGUNTA DO USUÁRIO:
    {query}

    CONTEXTO RECEBIDO:
    {context}
    """)

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
