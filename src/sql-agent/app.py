# sql_chat_app.py
import streamlit as st
from databricks_agent import ask

st.set_page_config(page_title="🔎 Databricks SQL Agent Chat", layout="centered")
st.title("📊 Agente de Análise SQL Databricks")
st.caption(
    "Sou um agente de dados que traduz suas perguntas para SQL e consulta o banco de dados 'financas_semantica'."
)

# 1. Inicializar o Histórico de Chat
if "sql_messages" not in st.session_state:
    st.session_state["sql_messages"] = [
        {
            "role": "assistant",
            "content": "Olá! Qual análise você gostaria de fazer no banco de dados financeiro? Tente algo como: 'Quais foram as vendas totais em 2025?'",
        }
    ]

# 2. Exibir o Histórico de Chat
for message in st.session_state["sql_messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. Capturar a Entrada do Usuário
if prompt := st.chat_input("Insira sua pergunta de SQL analítico..."):
    # Adicionar a mensagem do usuário ao histórico
    st.session_state["sql_messages"].append({"role": "user", "content": prompt})

    # Exibir a mensagem do usuário
    with st.chat_message("user"):
        st.markdown(prompt)

    # 4. Processar a Pergunta com o SQL Agent
    with st.chat_message("assistant"):
        with st.spinner("Gerando e executando consulta SQL no Databricks..."):
            try:
                # Chama a função do seu Agente SQL
                response = ask(prompt)

                # Exibe a resposta formatada
                st.markdown(response)

            except Exception as e:
                # Garante que o usuário veja o erro
                error_message = f"**Ocorreu um erro ao consultar o agente:**\n\n```text\n{e}\n```\n\n*Verifique se a tabela 'financas_semantica' e as conexões do Databricks estão configuradas corretamente no databricks-agent.py.*"
                st.error(error_message)
                response = f"Erro: {e}"

    # 5. Adicionar a Resposta do Assistente ao Histórico
    st.session_state["sql_messages"].append({"role": "assistant", "content": response})

# --- Sidebar ---
with st.sidebar:
    st.header("🔗 Conexão do Agente")
    st.markdown("""
        Este agente usa **LangChain SQL Agent Toolkit** para interagir com seu **Databricks SQL Warehouse**.
        - **LLM:** `gpt-4.1-mini` (definido em `databricks-agent.py`)
        - **Banco de Dados:** `financas_semantica`
    """)
    st.markdown("---")
