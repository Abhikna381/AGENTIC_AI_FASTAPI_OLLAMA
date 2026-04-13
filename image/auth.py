import jwt
import datetime

SECRET = "mysecretkey"

# fake users
users = {
    "admin": "1234",
    "user": "1234"
}

def authenticate_user(username, password):
    if username in users and users[username] == password:
        return {"username": username}
    return None


def create_access_token(data: dict):
    payload = {
        "sub": data["sub"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        return payload["sub"]
    except:
        return None