# 🌐 Consumindo Modelos Databricks com o OpenAI Client

Este projeto demonstra como interagir com um **LLM Endpoint** (Modelo Servido) no Databricks usando o cliente Python da OpenAI. Essa abordagem é possível porque o Databricks Model Serving adota a mesma especificação de API de *completion* de chat que a OpenAI.

## 🗺️ Roadmap de Configuração

### 1\. Preparação do Databricks LLM Endpoint

Antes de executar o código, você deve ter um LLM servido no seu Databricks Workspace:

1.  **Modelo Servido (LLM Endpoint):** Certifique-se de que o modelo que você deseja usar (ex: `databricks-meta-llama-3-1-405b-instruct`) está configurado e ativo em **Model Serving** no Databricks.
2.  **API URL (Base URL):** O endpoint que você usará como `base_url` no cliente OpenAI. O formato típico é:
    ```
    https://<DATABRICKS_HOST>/serving-endpoints
    ```
    *Para obter o endereço correto, acesse a página de detalhes do seu Endpoint de LLM no Databricks.*

### 2\. Configuração de Variáveis de Ambiente

Crie um arquivo `.env` para armazenar as credenciais necessárias.

| Variável | Descrição | Exemplo de Valor |
| :--- | :--- | :--- |
| `DATABRICKS_TOKEN` | Seu Token de Acesso Pessoal (PAT) do Databricks. **Este token será usado como `api_key` no cliente OpenAI.** | `dapi...` |
| `base_url` | O **Base URL** do seu LLM Endpoint (API URL). | `https://adb-XXX.cloud.databricks.com/serving-endpoints` |

### 3\. Instalação de Dependências

Você precisará apenas do cliente `openai` e do `python-dotenv`:

```bash
pip install openai python-dotenv
```

-----

## 💻 Explicação do Arquivo `serving-models-databricks.py`

O script demonstra como o cliente OpenAI é configurado para apontar para o Databricks em vez do serviço original da OpenAI.

### 1\. Configuração da Conexão

```python
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DATABRICKS_TOKEN"),
    base_url=os.getenv("base_url"),
)
```

| Parâmetro no `OpenAI(client=...)` | Valor Atribuído | Função |
| :--- | :--- | :--- |
| `api_key` | **`DATABRICKS_TOKEN`** | O Databricks utiliza o **Token de Acesso Pessoal (PAT)** como chave de autenticação (API Key) para acessar o serviço de Model Serving. |
| `base_url` | **`base_url`** | O endereço da API do Databricks (Ex: `https://.../serving-endpoints`). Isso redireciona todas as chamadas do cliente OpenAI para o seu ambiente Databricks. |

### 2\. Invocação do Modelo (Chat Completion)

A chamada para `client.chat.completions.create` é padrão da OpenAI, mas com algumas modificações cruciais.

```python
response = client.chat.completions.create(
    model="databricks-meta-llama-3-1-405b-instruct",
    messages=[{"role": "user", "content": "What is Databricks?"}],
    temperature=0,
    extra_body={"usage_context": {"project": "project1"}},
)
```

| Parâmetro | Função e Detalhe |
| :--- | :--- |
| `model` | Deve ser o **nome exato** do seu LLM Endpoint configurado no Databricks. |
| `messages` | O formato de entrada de chat padrão (lista de dicionários com `role` e `content`). |
| `temperature` | Controla a aleatoriedade da resposta (0 = determinística, 1 = criativa). |
| `extra_body` | **(Opcional, mas útil no Databricks)** Permite passar metadados, como `usage_context`, para fins de rastreamento de custos e monitoramento no seu Workspace. |

### 3\. Execução

Ao rodar o script, o cliente OpenAI enviará a requisição para o `base_url` (Databricks) usando o token como chave, e o Databricks retornará a resposta gerada pelo LLM.

```python
# Execução da resposta
answer = response.choices[0].message.content
print("Answer:", answer)
```

Este método simplifica a integração, permitindo que você utilize a vasta documentação e bibliotecas do ecossistema OpenAI, enquanto executa os modelos no seu ambiente Databricks seguro e escalável.