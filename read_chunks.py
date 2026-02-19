import os
import json
import pandas as pd
from openai import OpenAI
import time
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import joblib

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))   # API key env variable se read hogi


def create_embedding_batch(text_list):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text_list
    )
    return [item.embedding for item in response.data]


def batch_embeddings(texts, batch_size=500):  # ✅ batch_size changed to 500
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        print(f"Processing batch {i} to {i+len(batch)}")

        embeddings = create_embedding_batch(batch)
        all_embeddings.extend(embeddings)

        time.sleep(0.5)   # rate limit safety

    return all_embeddings


# ✅ Read ALL JSON files
jsons = os.listdir("newjsons")

all_chunks = []

for json_file in jsons:
    with open(f"newjsons/{json_file}", "r", encoding="utf-8") as f:
        content = json.load(f)

    print(f"Reading {json_file} — chunks:", len(content["chunks"]))

    for chunk in content["chunks"]:
        chunk["source_file"] = json_file   # track file name
        all_chunks.append(chunk)

print("\nTotal chunks collected from ALL files:", len(all_chunks))


# ✅ Create embeddings for all texts
texts = [c["text"] for c in all_chunks]

embeddings = batch_embeddings(texts, batch_size=500)  # ✅ batch size updated

print("Total embeddings received:", len(embeddings))


# ✅ Attach embeddings
for i, chunk in enumerate(all_chunks):
    chunk["chunk_id"] = i
    chunk["embedding"] = embeddings[i]

        
# ✅ Single DataFrame
df = pd.DataFrame.from_records(all_chunks)
joblib.dump(df,"embeddings.joblib")


# print("\nFinal DataFrame Shape:", df.shape)
