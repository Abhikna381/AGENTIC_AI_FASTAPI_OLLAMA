from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from openai import OpenAI
from dotenv import load_dotenv
import base64, os

from image.auth import authenticate_user, create_access_token, decode_token
from image.users import create_user
from image.database import SessionLocal, ChatMemory, UserImage

# ✅ FIX: load .env correctly
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

BASE_DIR = os.path.dirname(__file__)

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
from image.database import SessionLocal, User
from pydantic import BaseModel

class RegisterRequest(BaseModel):
    username: str
    password: str

@app.post("/register")
def register(data: RegisterRequest):

    print("REGISTER HIT:", data)

    db = SessionLocal()

    try:
        # check existing
        existing = db.query(User).filter(User.username == data.username).first()

        if existing:
            raise HTTPException(status_code=400, detail="User already exists")

        new_user = User(
            username=data.username,
            password=data.password
        )

        db.add(new_user)
        db.commit()

        print("USER SAVED SUCCESSFULLY")  # 👈 DEBUG

        return {"message": "User created"}

    except Exception as e:
        print("REGISTER ERROR:", str(e))   # 👈 CRITICAL DEBUG
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()

        
# ---------- LOGIN ----------
from image.database import SessionLocal, User

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):

    db = SessionLocal()

    user = db.query(User).filter(
        User.username == form_data.username
    ).first()

    if not user or user.password != form_data.password:
        db.close()
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.username})

    db.close()

    return {"access_token": token}

# ---------- CHAT ----------
@app.post("/chat")
def chat(data: dict, token: str = Depends(oauth2_scheme)):
    username = decode_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    if "message" not in data:
        raise HTTPException(status_code=400, detail="Message missing")

    db = SessionLocal()

    try:
        # last 5 chats
        history = db.query(ChatMemory)\
            .filter(ChatMemory.username == username)\
            .order_by(ChatMemory.id.desc())\
            .limit(5).all()

        context = "\n".join([f"{h.message} -> {h.response}" for h in history])

        # last image
        last_img = db.query(UserImage)\
            .filter(UserImage.username == username)\
            .order_by(UserImage.id.desc()).first()

        content = [
            {"type": "input_text", "text": f"""
User: {username}
Chat History:
{context}
Question: {data['message']}
"""}
        ]

        if last_img:
            content.append({
                "type": "input_image",
                "image_url": f"data:image/jpeg;base64,{last_img.image_data}"
            })

        response = client.responses.create(
            model="gpt-4o-mini",
            input=[{"role": "user", "content": content}]
        )

        # ✅ SAFE PARSE
        reply = response.output_text

        # save chat
        db.add(ChatMemory(
            username=username,
            message=data["message"],
            response=reply
        ))
        db.commit()

        return {"reply": reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()

# ---------- IMAGE ----------
@app.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    token: str = Depends(oauth2_scheme)
):
    username = decode_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    db = SessionLocal()

    try:
        img = await file.read()
        b64 = base64.b64encode(img).decode()

        # save image
        db.add(UserImage(username=username, image_data=b64))
        db.commit()

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

        caption = response.output_text

        return {"caption": caption}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()