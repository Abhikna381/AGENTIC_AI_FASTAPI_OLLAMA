from dotenv import load_dotenv
load_dotenv()
from image.database import engine

try:
    conn = engine.connect()
    print("✅ MySQL Connected!")
except Exception as e:
    print("❌ Error:", e)