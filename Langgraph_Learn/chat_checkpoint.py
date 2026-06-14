from dotenv import load_dotenv
from typing import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph,MessagesState, START, END
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.mongodb import MongoDBSaver


load_dotenv()

# Initialize the LLM
llm = init_chat_model(
    model = "gpt-4.1-mini",
    model_provider = "openai"
)


# State
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


# Chatbot Node
def chatbot(state: MessagesState):
    response = llm.invoke(state.get("messages"))
    return { "messages": [response]}
    #return {"messages": [{"role": "ai", "content": "Hi, This is a message from ChatBot Node"}]} 



# state = {messages: ["Hey there"]}
# node runs: chatbot(state: ["Hey there"]) -> ["Hi, This is a message from ChatBot Node"]
# state = {messages: ["Hey there", "Hi, This is a message from ChatBot Node"]}


    
# Create Graph
# (START) -> chatbot -> samplenode -> (END)

graph = StateGraph(MessagesState)
graph.add_node("chatbot", chatbot)



graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)


# graph = graph.compile() # You are compiling the graph twice, and 
                        # the first compile removes the ability to add the checkpointer later.
                        # After that, graph becomes a compiled graph object, so this later line fails conceptually


# Compile with Checkpointer
def compile_graph_with_checkpointer(checkpointer):
    
    # Because a compiled graph does not have .compile() again.
    return graph.compile(checkpointer=checkpointer)  


 
# MongoDB Connection
MONGODB_URI = "mongodb://admin:admin@localhost:27017"


with MongoDBSaver.from_conn_string(MONGODB_URI) as checkpointer:
    graph_with_checkpointer = compile_graph_with_checkpointer(checkpointer=checkpointer)

    '''updated_state = graph_with_checkpointer.invoke(
        {
            "messages": [
                                    {
                                        "role": "user", 
                                        "content": "What is my name ?"
                                    }
                                ]
                            },
                            {
                                         "configurable": {
                                                "thread_id": "AKSHAT"
                                        }
                            }
                        )
    print("\n\nupdated_state", updated_state)'''


    for chunk in graph_with_checkpointer.stream(
        {
            "messages": [
                                    {
                                        "role": "user", 
                                        "content": "what is my Name ?"
                                    }
                                ]
                            },

                            {
                                         "configurable": {
                                                "thread_id": "AKSHAT"
                                        }
                            },

                            stream_mode= "values"
                        ):
        chunk["messages"][-1].pretty_print()
    # print("\n\nupdated_state", updated_state)




#updated_state = graph.invoke(MessagesState({"messages": ["Hi, I am Abhijeet ..."]}))
#updated_state = graph.invoke({"messages": [{"role": "user", "content": "What is my name ?"}]})
#print("\n\nupdated_state", updated_state)


# node runs: chatbot(state: ["hey There"]) -> ["Hi, This is a message from Chatbot Node"]




# Checkpointer (Akshat) = Hey My name is Abhi