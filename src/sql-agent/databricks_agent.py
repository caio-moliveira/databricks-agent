import os
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import create_sql_agent
from db import engine


CATALOG = "ai-agent-workshop"
SCHEMA = "data"
VIEW = f"{CATALOG}.{SCHEMA}.financas_vendas"


# 1) Conecta ao Warehouse
db = SQLDatabase(
    engine,
    include_tables=["financas_vendas"],
)

# 2) LLM (troque por seu provedor preferido)
llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

# 3) Toolkit + agente
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

SYSTEM_PROMPT_PT = """
Você é um analista de dados que responde em português, gerando apenas SQL compatível com Databricks SQL
quando precisar consultar dados.
Traga a resposta sempre no formato de texto, não em tabelas.

"""

agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    agent_type="openai-tools",
    verbose=True,
    handle_parsing_errors=True,
    system_message=SYSTEM_PROMPT_PT,
    top_k=5,
)


def ask(question: str) -> str:
    """Chame isto do seu endpoint/UI."""
    return agent.run(question)
