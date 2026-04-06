import subprocess
import sys # 1. Import sys

def run_rag_pipeline():
    # 2. Capture the path of the current Python interpreter
    python_path = sys.executable 

    print("--- Starting Indexing ---")
    # 3. Use python_path instead of the string "python"
    subprocess.run([python_path, "index.py"], check=True)
    
    print("\n--- Starting Chat Interface ---")
    subprocess.run([python_path, "chat.py"], check=True)

if __name__ == "__main__":
    run_rag_pipeline()