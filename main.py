# pip install databricks-langchain langchain mlflow

import os
from operator import itemgetter
from typing import Any, Dict

from databricks_langchain import DatabricksVectorSearch, ChatDatabricks
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableMap
from langchain_core.output_parsers import StrOutputParser
import mlflow

# 1) Configure seus endpoints/nomes (substitua pelos reais)
VS_ENDPOINT = os.getenv(
    "VS_ENDPOINT", "meu-vs-endpoint"
)  # nome do endpoint de Vector Search
INDEX_NAME = os.getenv(
    "VS_INDEX", "catalog.schema.index_name"
)  # caminho completo do índice
LLM_ENDPOINT = os.getenv("LLM_EP", "databricks-meta-llama-3-3-70b-instruct")
MODEL_NAME = os.getenv("MODEL_NAME", "langchain_rag_demo")


# 2) Função que carrega o retriever (usada pela cadeia e pelo MLflow)
def retriever_loader():
    index = DatabricksVectorSearch(
        endpoint=VS_ENDPOINT,
        index_name=INDEX_NAME,
        columns=["ID", "TEXT"],  # ajuste se no seu índice os nomes diferirem
    )
    return index.as_retriever(search_kwargs={"k": 3, "query_type": "HYBRID"})


retriever = retriever_loader()

# 3) Prompt simples (ajuste para instruções/RAG de verdade)
prompt = PromptTemplate.from_template(
    "Responda de forma concisa.\n\nPergunta: {query}\n\nContexto:\n{context}\n\nResposta:"
)


# 4) Funções auxiliares
def ensure_query(input_: Dict[str, Any]) -> str:
    """Extrai a pergunta. Se vier como 'messages' (string), usa direto."""
    msg = input_.get("messages", "")
    # Se fosse lista de mensagens tipo chat, aqui você transformaria em string.
    return msg if isinstance(msg, str) else str(msg)


def format_context(chunks: Any) -> str:
    """Transforma a lista de Document(s) do retriever em um bloco de texto."""
    if chunks is None:
        return ""
    try:
        # LangChain retriever retorna uma lista de Document
        return "\n\n---\n\n".join(getattr(d, "page_content", str(d)) for d in chunks)
    except Exception:
        return str(chunks)


# 5) LLM no Model Serving
llm = ChatDatabricks(endpoint=LLM_ENDPOINT)

# 6) Cadeia LCEL
chain = (
    RunnableMap(
        {
            "query": RunnableLambda(ensure_query),
            "context": RunnableLambda(ensure_query)
            | retriever
            | RunnableLambda(format_context),
        }
    )
    | prompt
    | llm
    | StrOutputParser()
)

# 7) Exemplo de chamada
input_example = {"messages": "O que é RCM e como aplicar?"}
resp = chain.invoke(input_example)
print(resp)

# 8) Log no MLflow (inclui como reconstruir o retriever)
with mlflow.start_run(run_name="rag-demo") as run:
    mlflow.langchain.log_model(
        chain,
        loader_fn=retriever_loader,
        artifact_path="rag_chain",
        registered_model_name=MODEL_NAME,
        input_example=input_example,
    )
