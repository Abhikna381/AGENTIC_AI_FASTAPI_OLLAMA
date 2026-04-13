from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer
from openai import OpenAI
import base64
import os

from image.auth import create_access_token, decode_token
from image.users import create_user, authenticate_user
from image.memory import add_memory, search_memory

app = FastAPI()
client = OpenAI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

BASE_DIR = os.path.dirname(__file__)

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- UI ----------------
@app.get("/")
def home():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

@app.get("/favicon.ico")
def favicon():
    return FileResponse(os.path.join(BASE_DIR, "favicon.ico"))

# ---------------- REGISTER ----------------
@app.post("/register")
def register(data: dict):
    user = create_user(data["username"], data["password"])

    if not user:
        raise HTTPException(status_code=400, detail="User already exists")

    return {"message": "User registered successfully"}

# ---------------- LOGIN ----------------
@app.post("/login")
def login(data: dict):
    user = authenticate_user(data["username"], data["password"])

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user["username"]})
    return {"access_token": token}

# ---------------- CHAT (RAG) ----------------
@app.post("/chat")
def chat(data: dict, token: str = Depends(oauth2_scheme)):
    username = decode_token(token)

    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    msg = data["message"]

    memories = search_memory(msg)
    context = "\n".join(memories)

    response = client.responses.create(
        model="gpt-4.1",
        input=[{
            "role": "user",
            "content": f"""
User: {username}

Memory:
{context}

Question:
{msg}
"""
        }]
    )

    reply = response.output[0].content[0].text

    add_memory(msg + " -> " + reply)

    return {"reply": reply}

# ---------------- IMAGE CAPTION ----------------
@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    img = await file.read()
    b64 = base64.b64encode(img).decode()

    response = client.responses.create(
        model="gpt-4.1",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Describe this image"},
                {"type": "input_image", "image_url": f"data:image/jpeg;base64,{b64}"}
            ]
        }]
    )

    caption = response.output[0].content[0].text

    add_memory("image caption: " + caption)

    return {"caption": caption}