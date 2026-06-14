from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def index():
    return {"message": "Hello, I am Abhi!",
            
            "description": "I am a RAG (Retrieval Augmented Generation) based AI assistant built using FastAPI and OpenAI's GPT-5 model. I can answer your queries based on the context retrieved from a PDF file, including page contents and page numbers. Feel free to ask me anything!",
            
            "usage": "To use this API, send a GET request to the /ask endpoint with your query as a parameter. For example: /ask?query=What is RAG?",
            
            "author": "Abhi",
            
            "version": "1.0",
            
            "contact": "+911234567890",
            
            "email": "123456789@x.com",
            
            "github": "https://github.com/abhi",
            
            "linkedin": "https://linkedin.com/in/abhi",
            
            "twitter": "https://twitter.com/abhi"
            }