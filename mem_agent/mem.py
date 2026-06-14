from dotenv import load_dotenv
from mem0 import Memory
import os
import json


from openai import OpenAI

load_dotenv()  # Load environment variables from .env file

client = OpenAI()  # Initialize OpenAI client

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")   


config = {
    "version": "v1.0",
    "embedder": {
        "provider": "openai",
        "config": {"api_key": OPENAI_API_KEY, "model": "text-embedding-3-small"}
    },

    "llm": {
        "provider": "openai",
        "config": {"api_key": OPENAI_API_KEY, "model": "gpt-4.1-mini" }
    },

    "graphstore": {
        "provider": "neo4j",
        "config": {
            "url": os.getenv("NEO_CONNECTION_URI"),
            "username": os.getenv("NEO_USERNAME"),
            "password": os.getenv("NEO_PASSWORD")
        }
    },

    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": "memories"
        }
    }
}


mem_client = Memory.from_config(config)

while True:

    user_query = input("> ")

    search_memory = mem_client.search(query = user_query, 
                                      filters={"user_id": "ABHI"}
                                      )

    memories = [
        f"ID: {mem.get('id')}\nMemory: {mem.get('memory')}"
        for mem in search_memory.get("results")
    ]

    print("FoundMemories", memories)

    SYSTEM_PROMPT = f"""
       Here is the context about the user:
       {json.dumps(memories)}
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query}
        ]
    )

    ai_response = response.choices[0].message.content

    print("AI Response:", ai_response)

    mem_client.add(
        user_id = "ABHI",
        messages = [
            {"role": "user", "content": user_query},
            {"role": "assistant", "content": ai_response}
        ]
    )

    print("Memory added to vector store.")

