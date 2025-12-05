# main.py
import os
from dotenv import load_dotenv


class Settings:
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
    DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")

    # DATABRICKS_ACCOUNT_ID = os.getenv("DATABRICKS_ACCOUNT_ID")
    MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "databricks")
    EXPERIMENT_ID = os.getenv("EXPERIMENT_ID")

    VS_ENDPOINT = os.getenv("VS_ENDPOINT", "my-vector-search")
    INDEX_NAME = os.getenv("VS_INDEX", "ai-agent-workshop.data.produtos_index")
    LLM_ENDPOINT = os.getenv("LLM_EP", "databricks-meta-llama-3-3-70b-instruct")
    MODEL_NAME = os.getenv("MODEL_NAME", "langchain_rag_demo")
    DATABRICKS_HTTP_PATH = os.getenv(
        "HTTP_PATH", "/sql/1.0/warehouses/92070bb914c32dff"
    )


settings = Settings()
