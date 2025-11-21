# main.py
import os
import mlflow
from databricks_langchain import DatabricksVectorSearch, ChatDatabricks
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableMap
from langchain_core.output_parsers import StrOutputParser

# --- CONFIG (use variáveis de ambiente fora do código em prod) ---
os.environ["DATABRICKS_HOST"] = ""
os.environ["DATABRICKS_TOKEN"] = ""
os.environ["MLFLOW_TRACKING_URI"] = "databricks"
EXPERIMENT_ID = os.getenv("EXPERIMENT_ID", "")

VS_ENDPOINT = os.getenv("VS_ENDPOINT", "my-vector-db")
INDEX_NAME = os.getenv("VS_INDEX", "agent.gpt.products_vs_index")
LLM_ENDPOINT = os.getenv("LLM_EP", "databricks-meta-llama-3-3-70b-instruct")
MODEL_NAME = os.getenv("MODEL_NAME", "langchain_rag_demo")

# --- Retriever (1 linha prática) ---
retriever = DatabricksVectorSearch(
    endpoint=VS_ENDPOINT,
    index_name=INDEX_NAME,
    columns=["id", "description"],  # ajuste ao nome das suas colunas
).as_retriever(search_kwargs={"k": 3, "query_type": "HYBRID"})

# --- Prompt + LLM + Cadeia ---
prompt = PromptTemplate.from_template(
    "Responda de forma concisa.\n\nPergunta: {query}\n\nContexto:\n{context}\n\nResposta:"
)


def ensure_query(d):
    return d.get("messages", "")


def format_ctx(docs):
    return (
        ""
        if not docs
        else "\n\n---\n\n".join(getattr(x, "page_content", str(x)) for x in docs)
    )


llm = ChatDatabricks(endpoint=LLM_ENDPOINT)

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

# --- Teste rápido ---
print(chain.invoke({"messages": "What is the description of product id 2?"}))

# --- Log no MLflow (sem classe, direto) ---
mlflow.set_experiment(experiment_id=EXPERIMENT_ID)
with mlflow.start_run(run_name="rag-demo"):
    model_info = mlflow.langchain.log_model(
        lc_model=chain,
        loader_fn=lambda: retriever,
        name="rag_chain",
        registered_model_name=MODEL_NAME,
    )
    print("Model logged at:", model_info.model_uri)
