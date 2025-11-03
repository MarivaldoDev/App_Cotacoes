import threading

import yfinance
from customtkinter import *
from decouple import config
from langchain.agents import create_tool_calling_agent
from langchain.agents.agent import AgentExecutor
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq


api_key = config("API_KEY")
llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key)


class App:
    def __init__(self):
        self.window()

    def window(self):
        self.tela = CTk()
        self.tela.resizable(False, False)
        self.tela.geometry("420x350")
        self.tela.title("Interface de Cotação")

        self.label = CTkLabel(self.tela, text="Cotação", font=("Arial", 20))
        self.label.place(x=30, y=25)

        self.input_field = CTkEntry(
            self.tela, width=200, height=35, placeholder_text="Digite a cotação ou ação"
        )
        self.input_field.place(x=30, y=60)

        self.button = CTkButton(
            self.tela, text="Buscar", command=self.executar_agente_thread
        )
        self.button.place(x=150, y=120)

        self.frame = CTkFrame(self.tela, width=360, height=150, fg_color="#D3D3D3")
        self.frame.place(x=30, y=180)

        self.resultado = CTkLabel(
            self.frame,
            text="",
            font=("Arial", 16),
            text_color="black",
            wraplength=320,
            anchor="w",
            justify="left",
        )
        self.resultado.place(x=20, y=50)

        self.tela.mainloop()


    def executar_agente_thread(self):
        thread = threading.Thread(target=self.agente_ia)
        thread.start()


    @tool
    def buscar_cotacao(cotacao: str) -> float:
        """Retorna a cotação da moeda informada. Porém você deve informar a sigla da moeda de acordo o padrão do yahoofinance, por exemplo: USDBRL=X, EURBRL=X, BTC-USD, GC=F"""
        dados = yfinance.Ticker(f"{cotacao}").info
        cotacao_atual = dados["regularMarketPrice"]

        return f"R$ {cotacao_atual:.2f}"

    def agente_ia(self):
    # Atualiza o label existente em vez de destruí-lo — mantém a configuração
    # de wraplength (quebra automática de linha) para evitar overflow.
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

        cotacao = self.input_field.get()
        comando = f"Me informe a cotação atual da moeda {cotacao}."
        mensagens.append(("human", comando))

        mensagens.append(MessagesPlaceholder(variable_name="agent_scratchpad"))

        prompt = ChatPromptTemplate.from_messages(mensagens)

        tools = [self.buscar_cotacao]

        agent = create_tool_calling_agent(llm, tools, prompt)
        executor = AgentExecutor.from_agent_and_tools(
            agent=agent, tools=tools, verbose=True
        )

        try:
            resposta = executor.invoke({"input": comando})
            saida = resposta["output"]
            # Atualiza o texto do label já existente; o wraplength evita que o texto
            # ultrapasse a largura do frame.
            self.resultado.configure(text=saida)
        except Exception as e:
            print(f"[Erro ao executar agente]: {e}")


App()
