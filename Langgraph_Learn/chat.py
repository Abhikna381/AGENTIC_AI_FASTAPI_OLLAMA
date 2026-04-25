from dotenv import load_dotenv
from typing import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph,MessagesState, START, END
from langchain.chat_models import init_chat_model

load_dotenv()


llm = init_chat_model(
    model = "gpt-4.1-mini",
    model_provider = "openai"
)


class State(TypedDict):
    messages: Annotated[list, add_messages]


'''def chatbot(state):
    model = init_chat_model("openai:gpt-4o-mini")

    response = model.invoke(state["messages"])

    return {
        "messages": [
            {"role": "assistant", "content": response.content}
        ]
    }'''


def chatbot(state: MessagesState):
    response = llm.invoke(state.get("messages"))
    return { "messages": [response]}
    #return {"messages": [{"role": "ai", "content": "Hi, This is a message from ChatBot Node"}]} 



# state = {messages: ["Hey there"]}
# node runs: chatbot(state: ["Hey there"]) -> ["Hi, This is a message from ChatBot Node"]
# state = {messages: ["Hey there", "Hi, This is a message from ChatBot Node"]}

def samplenode(state: MessagesState):
    print("\n\nInside samplenode node", state)
    return { "messages": ["Sample Message Appended"]}
    

# (START) -> chatbot -> samplenode -> (END)

graph = StateGraph(MessagesState)
graph.add_node(chatbot)
graph.add_node(samplenode)


graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", "samplenode")
graph.add_edge("samplenode", END)

graph = graph.compile()

updated_state = graph.invoke({"messages": [{"role": "user", "content": "hi!"}]})
print("\n\nupdated_state", updated_state)