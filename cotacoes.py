import yfinance
from decouple import config
from langchain.agents import create_tool_calling_agent
from langchain.agents.agent import AgentExecutor
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq


@tool
def buscar_cotacao(cotacao: str) -> float:
    """Retorna a cotação da moeda informada. Porém você deve informar a sigla da moeda de acordo o padrão do yahoofinance, por exemplo: USDBRL=X, EURBRL=X, BTC-USD, GC=F"""
    dados = yfinance.Ticker(f"{cotacao}").info
    cotacao_atual = dados["regularMarketPrice"]

    return f"R$ {cotacao_atual:.2f}"


api_key = config("API_KEY")
llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key)


cotacao = str(input("Qual a cotação que você deseja consultar: ")).strip().lower()
mensagens = [
    (
        "system",
        (
            "Você é um assistente especializado em cotações de moedas, especificamente da plataforma yahoofinace. "
            "Sua tarefa é fornecer a cotação atual da moeda solicitada pelo usuário. "
            "Utilize a ferramenta 'buscar_cotacao' para obter a cotação correta. "
            "Lembre-se de sempre responder de forma clara e objetiva."
            "Se a cotação for uma 'ação', sempre adicione o '.SA' ao final da sigla da ação para buscar a cotação correta, e não coloque o 'BRL=X' ao final."
        ),
    ),
]

comando = f"Me informe a cotação atual da moeda {cotacao}."
mensagens.append(("human", comando))

mensagens.append(MessagesPlaceholder(variable_name="agent_scratchpad"))

prompt = ChatPromptTemplate.from_messages(mensagens)


tools = [buscar_cotacao]

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True)

try:
    resposta = executor.invoke(
        {"input": comando} 
    )
    print(resposta["output"])
except Exception as e:
    print(f"[Erro ao executar agente]: {e}")
