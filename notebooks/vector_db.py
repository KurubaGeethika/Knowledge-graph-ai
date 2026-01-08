# generaate embeddings
from openai import OpenAI
import pandas as pd

client = OpenAI(api_key="YOUR_API_KEY")
df = pd.read_csv("apple_prompt_response_1000_realistic.csv")

records = []

for _, row in df.iterrows():
    text_to_embed = row["prompt"] + " " + row["response"]
    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=text_to_embed
    )["data"][0]["embedding"]
    
    record = {
        "id": row["run_id"],        # unique id
        "vector": embedding,        # embedding vector
        "metadata": {
            "prompt_id": row["prompt_id"],
            "topic": row["topics"],
            "theme": row["themes"],
            "region": row["region"],
            "model": row["model"],
            "citations": row["citations"]
        },
        "text": text_to_embed
    }
    records.append(record)


# insert embeddings to db 
from chromadb import Client
from chromadb.config import Settings

client = Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="./chroma_db"))
collection = client.create_collection("apple_prompts")

for rec in records:
    collection.add(
        ids=[rec["id"]],
        embeddings=[rec["vector"]],
        metadatas=[rec["metadata"]],
        documents=[rec["text"]]
    )
