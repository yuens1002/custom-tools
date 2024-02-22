"""GmailToolkit Template"""
from langchain.agents import (AgentExecutor, create_openai_functions_agent, Tool)
# langchain agent main'
from sayvai_tools.tools import GetDate
from langchain_community.agent_toolkits import GmailToolkit
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
# Create a new LangChain instance
llm = ChatOpenAI(model="gpt-3.5-turbo-0125")

# instructions = """You are an assistant who used to help to perform all action related to Gmail."""
# base_prompt = hub.pull("langchain-ai/openai-functions-template")
# print(base_prompt)
# prompt = base_prompt.partial(instructions=instructions)

_SYSTEM_PROMPT: str = (
    """You are an assistant for SayvAI Software LLP. You are asked to perform based on the user's request.
    You can use following tools to perform the actions:

    <Tools>
    1) GmailCreateDraft - Create a draft email
    2) GmailSendMessage - Send a message
    3) GmailSearch - Search for emails
    4) GmailGetMessage - Get a message 
    5) GmailGetThread - Get a thread
    5) GetDate - Get current date and time (returns only current date and time, utilise current date and time to calculate future or past date and time)
    </Tools>

    Rules:- 
    1) Always talk about SayvAI Software LLP.
    2) IF user asks about get me tommorow's mail /messages (respond with it is not possible )


    """
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", _SYSTEM_PROMPT),
        ("human", "{agent_memory} {input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ]
)

class SayvaiDemoAgent:

    def __init__(self):
        self.llm = llm
        self.prompt = prompt
        self.tools = None
        self.gmailkit = GmailToolkit()
        self.memory = ConversationBufferWindowMemory(
            memory_key="agent_memory",
            window_size=10,
        )
        
    def initialize_tools(self) -> str:
        self.tools = self.gmailkit.get_tools()
        self.tools.append(
            Tool(
                    func=GetDate()._run,
                    name="GetDateTool",
                    description="""A tool that takes no input and returns the current date and time."""
                ),

        )    
        return "Tools Initialized"

    def initialize_agent_executor(self) -> AgentExecutor:
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            prompt=self.prompt,
            tools=self.tools,
        )
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            memory=self.memory
        )
        return "Agent Executor Initialized"

    def invoke(self, message) -> str:
        return self.agent_executor.invoke(input={"input": message})["output"]

