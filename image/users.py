# users.py

# TEMP DATABASE (you can later replace with MySQL/PostgreSQL)
USERS_DB = {
    "admin": {
        "username": "admin",
        "password": "admin123"
    },
    "ankita": {
        "username": "ankita",
        "password": "12345"
    }
}


def get_user(username: str):
    return USERS_DB.get(username)


def create_user(username: str, password: str):
    if username in USERS_DB:
        return False

    USERS_DB[username] = {
        "username": username,
        "password": password
    }
    return True