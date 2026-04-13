from datetime import datetime, timedelta
import jwt

SECRET_KEY = "mysecretkey123"
ALGORITHM = "HS256"

# demo user (replace with DB later)
USERS = {
    "admin": "admin123"
}

def authenticate_user(username, password):
    if username in USERS and USERS[username] == password:
        return {"username": username}
    return None


def create_access_token(data: dict, expires_minutes=60):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except:
        return None