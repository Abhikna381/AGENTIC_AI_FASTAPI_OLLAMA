users_db = {}

def create_user(username, password):
    if username in users_db:
        return None

    users_db[username] = {
        "username": username,
        "password": password
    }
    return users_db[username]

def get_user(username):
    return users_db.get(username)