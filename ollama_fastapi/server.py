from fapi import FastAPI,Body
from ollama import Client

app = FastAPI()

client = Client(
    host = "http://localhost:11434",
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/ANKITA")
def read_root():
    return {"GUNU HAUCHI ANKITA AAU MORA CHUA"}

@app.post("/chat")
def chat(
        message: str = Body(..., description="The Message")
):
    response = client.chat(model = "gemma:2b", messages=[
        {"role": "user", "content": message}
    ])

    return {"response": response.message.content}