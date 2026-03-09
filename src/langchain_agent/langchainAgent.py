from promptEngineering.config import * 
# chat prompt not instructed prompt, as agent need to loop the tools and steps
from langchain import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# import agents 
from langchain.agents import create_openai_functions_agent, create_openai_tools_agent, AgentExecutor
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage, AIMessage
from langchain.tools.retriever import create_retriever_tool

from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain import OpenAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS

# Create Retriever
loader = WebBaseLoader("https://python.langchain.com/docs/expression_language/")
docs = loader.load()
    
splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=20
)
splitDocs = splitter.split_documents(docs)

embedding = OpenAIEmbeddings()
vectorStore = FAISS.from_documents(docs, embedding=embedding)
retriever = vectorStore.as_retriever(search_kwargs={"k": 3})

llm = ChatOpenAI(
    model=CONFIG["LLM"]["model"],
    temperature=CONFIG["LLM"]["temperature"]
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly assistant called FaZe Clan."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    # agent_scratchpad: Data processing for the intermediate steps, 
    # This should be pretty tightly coupled to the instructions in the prompt.
    MessagesPlaceholder(variable_name="agent_scratchpad")
])


# to execute the agent, it requrires at lease one tool, there create 2 tools: 
# Tavily's Search API is a search engine built for LLMs, delivering real-time, accurate results.
search = TavilySearchResults()
retriever_tools = create_retriever_tool(
    retriever,
    "lcel_search",
    "Use this tool when searching for information about Langchain Expression Language (LCEL)."
)
tools = [search, retriever_tools]

# defines the agent, 
agent = create_openai_functions_agent(
    llm=llm,
    prompt=prompt,
    tools=tools
)

# executor is for doing the work, execute the defination of the agent
agentExecutor = AgentExecutor(
    agent=agent,
    tools=tools
)

def process_chat(agentExecutor, user_input, chat_history):
    response = agentExecutor.invoke({
        "input": user_input,
        "chat_history": chat_history
    })
    return response["output"]

if __name__ == '__main__':
    chat_history = []

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break

        response = process_chat(agentExecutor, user_input, chat_history)
        chat_history.append(HumanMessage(content=user_input))
        chat_history.append(AIMessage(content=response))

        print("Assistant:", response)