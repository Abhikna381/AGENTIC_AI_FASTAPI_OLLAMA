from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from openai import OpenAI
from dotenv import load_dotenv
import base64
import os

from memory import add_memory, search_memory

load_dotenv()

app = FastAPI()
client = OpenAI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(__file__)

# UI
@app.get("/")
def home():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

# favicon
@app.get("/favicon.ico")
def favicon():
    return FileResponse(os.path.join(BASE_DIR, "favicon.ico"))

# IMAGE CAPTION
@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    img = await file.read()
    b64 = base64.b64encode(img).decode()

    response = client.responses.create(
        model="gpt-4.1",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Generate captions"},
                {"type": "input_image", "image_url": f"data:image/jpeg;base64,{b64}"}
            ]
        }]
    )

    return {"caption": response.output[0].content[0].text}


# 🧠 CHAT WITH MEMORY (RAG)
@app.post("/chat")
async def chat(data: dict):
    msg = data["message"]

    memories = search_memory(msg)
    context = "\n".join(memories)

    response = client.responses.create(
        model="gpt-4.1",
        input=[{
            "role": "user",
            "content": f"""
Memory:
{context}

User: {msg}
"""
        }]
    )

    reply = response.output[0].content[0].text

    add_memory(msg + " -> " + reply)

    return {"reply": reply}