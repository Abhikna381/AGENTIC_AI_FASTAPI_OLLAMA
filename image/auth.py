import jwt
import datetime
from users import get_user

SECRET_KEY = "mysecretkey"


def authenticate_user(username, password):
    user = get_user(username)

    if not user:
        return None

    if user["password"] != password:
        return None

    return user


def create_access_token(data):
    payload = {
        "sub": data["sub"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=10)
    }

    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except:
        return None