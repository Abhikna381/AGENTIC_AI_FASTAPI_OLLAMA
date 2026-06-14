from fastapi import FastAPI
from pydantic import BaseModel


class User(BaseModel):
    name: str
    id: int


app = FastAPI()


@app.get("/users", response_model=User)
def get_users():
    return User(name="Abhi", id=1)
