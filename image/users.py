from image.database import SessionLocal, User

def create_user(username, password):
    db = SessionLocal()

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        return None

    user = User(username=username, password=password)
    db.add(user)
    db.commit()
    db.close()

    return user


def get_user(username):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()
    return user