from dotenv import load_dotenv
load_dotenv()

import os
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

print("DEBUG DB URL:", DATABASE_URL)  # 👈 add this

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

# ---------- USER ----------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password = Column(String(100))


# ---------- CHAT MEMORY ----------
class ChatMemory(Base):
    __tablename__ = "chat_memory"

    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    message = Column(Text)
    response = Column(Text)


# ---------- IMAGE ----------
class UserImage(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    image_data = Column(Text)  # base64

try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")
except Exception as e:
    print("❌ DB Connection Failed:", e)