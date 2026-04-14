import jwt
import os
from datetime import datetime, timedelta

SECRET = os.getenv("JWT_SECRET", "secret")

def authenticate_user(username, password):
    from image.users import get_user
    user = get_user(username)
    if user and user["password"] == password:
        return user
    return None

def create_access_token(data: dict):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=6)
    return jwt.encode(payload, SECRET, algorithm="HS256")

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        return payload.get("sub")
    except:
        return None