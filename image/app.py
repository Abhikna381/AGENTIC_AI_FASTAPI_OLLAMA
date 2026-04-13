from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import base64
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
client = OpenAI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(__file__)

# Home page
@app.get("/")
def home():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

# Favicon
@app.get("/favicon.ico")
def favicon():
    return FileResponse(os.path.join(BASE_DIR, "favicon.ico"))

# Image Caption API
@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        content_type = file.content_type

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": """Analyze this image and generate 3 captions:
Creative:
Formal:
Funny:"""
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:{content_type};base64,{base64_image}",
                        },
                    ],
                }
            ],
        )

        result = response.output[0].content[0].text.strip()
        return {"caption": result}

    except Exception as e:
        print("ERROR:", e)
        return {"caption": "Error occurred"}