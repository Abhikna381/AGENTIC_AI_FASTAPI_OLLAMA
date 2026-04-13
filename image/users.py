import bcrypt

users_db = {}

def hash_password(password: str):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_user(username: str, password: str):
    if username in users_db:
        return None

    users_db[username] = {
        "username": username,
        "password": hash_password(password)
    }
    return users_db[username]

def authenticate_user(username: str, password: str):
    user = users_db.get(username)

    if not user:
        return None

    if verify_password(password, user["password"]):
        return user

    return None