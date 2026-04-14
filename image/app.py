from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from openai import OpenAI
from dotenv import load_dotenv

import base64, os

from image.memory import add_memory, search_memory
from image.auth import authenticate_user, create_access_token, decode_token
from image.users import create_user

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ✅ FIX PATH
BASE_DIR = os.path.dirname(__file__)

last_image = {"b64": None}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- HOME ----------
@app.get("/")
def home():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

# ---------- REGISTER ----------
@app.post("/register")
def register(data: dict):
    user = create_user(data["username"], data["password"])
    if not user:
        raise HTTPException(status_code=400, detail="User exists")
    return {"message": "User created"}

# ---------- LOGIN ----------
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user["username"]})
    return {"access_token": token}

# ---------- CHAT ----------
@app.post("/chat")
def chat(data: dict, token: str = Depends(oauth2_scheme)):
    username = decode_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    msg = data["message"]

    memories = search_memory(msg)
    context = "\n".join(memories)

    content = [
        {"type": "input_text", "text": f"""
User: {username}

Memory:
{context}

Question:
{msg}
"""}
    ]

    if last_image["b64"]:
        content.append({
            "type": "input_image",
            "image_url": f"data:image/jpeg;base64,{last_image['b64']}"
        })

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[{"role": "user", "content": content}]
    )

    reply = response.output[0].content[0].text

    add_memory(msg + " -> " + reply)

    return {"reply": reply}

# ---------- IMAGE ----------
@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    img = await file.read()
    b64 = base64.b64encode(img).decode()

    last_image["b64"] = b64

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Describe this image in detail"},
                {"type": "input_image", "image_url": f"data:image/jpeg;base64,{b64}"}
            ]
        }]
    )

    caption = response.output[0].content[0].text

    return {"caption": caption}