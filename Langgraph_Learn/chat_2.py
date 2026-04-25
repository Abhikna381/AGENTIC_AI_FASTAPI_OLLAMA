from dotenv import load_dotenv
from typing import TypedDict, Optional, Literal
from langgraph.graph import StateGraph, START, END
from openai import OpenAI



load_dotenv()


client = OpenAI()

class State(TypedDict):
    user_query: str
    llm_output : Optional[str]
    is_good: Optional[bool]




def chatbot(state: State):
    print("ChatBot Node",state)
    response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "user", "content": state.get("user_query")}
    ]
)

    state["llm_output"] = response.choices[0].message.content
    return state


    '''response = client.responses.create(
    model="gpt-4.1-mini",
    input=state.get("user_query")
)

    state["llm_output"] = response.output[0].content[0].text'''

def evaluate_response(state: State) -> Literal["chatbot_gemini", "endnode"]:
    print("evaluate_response Node",state)
    if False:
        return "endnode"
    
    return "chatbot_gemini"

def chatbot_gemini(state: State):
    print("chatbot_gemini Node",state)
    response = client.chat.completions.create(
    model="gpt-4.1",
    messages=[
        {"role": "user", "content": state.get("user_query")}
    ]
)

    state["llm_output"] = response.choices[0].message.content
    return state



def endnode(state: State):
    print("endnode Node",state)
    return state

graph = StateGraph(State)

graph.add_node(chatbot)
graph.add_node(chatbot_gemini)
graph.add_node(endnode)

graph.add_edge(START, "chatbot")
graph.add_conditional_edges("chatbot", evaluate_response)


graph.add_edge("chatbot_gemini", "endnode")
graph.add_edge("endnode", END)

graph = graph.compile()


updated_state = graph.invoke({"user_query": "Hey, what is 2+2 ?"})
print(updated_state)
