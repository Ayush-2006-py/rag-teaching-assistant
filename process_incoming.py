import os
import re
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ----------------- Load DB -----------------
df = joblib.load("embeddings.joblib").copy()

required_cols = {"title", "number", "start", "end", "text", "embedding"}
missing = required_cols - set(df.columns)
if missing:
    raise ValueError(f"embeddings.joblib missing columns: {missing}")

# ----------------- Cleaning helpers -----------------
def normalize_number(x):
    if pd.isna(x):
        return None
    s = str(x).strip().lower()
    m = re.search(r"\d+", s)
    return int(m.group()) if m else None

def normalize_text(x):
    return "" if pd.isna(x) else str(x)

df["title"] = df["title"].apply(normalize_text)
df["text"] = df["text"].apply(normalize_text)
df["number"] = df["number"].apply(normalize_number)

# drop bad rows
df = df[df["number"].notna()].reset_index(drop=True)

# ----------------- Embeddings (OpenAI) -----------------
def create_embedding_batch(text_list):
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=text_list
    )
    return [item.embedding for item in resp.data]

# ----------------- Hybrid retrieval -----------------
def build_keyword_score(frame: pd.DataFrame, query: str) -> np.ndarray:
    q = query.lower().strip()
    tokens = [t for t in re.findall(r"[a-zA-Z0-9<>/]+", q) if len(t) >= 3]

    blob = (frame["title"].fillna("") + " " + frame["text"].fillna("")).str.lower()

    score = np.zeros(len(frame), dtype=float)
    for t in tokens:
        score += blob.str.contains(re.escape(t)).astype(float).to_numpy()

    if score.max() > 0:
        score = score / score.max()
    return score

def wants_earliest(query: str) -> bool:
    q = query.lower()
    triggers = ["where", "taught", "covered", "which video", "kis video", "kahan", "kaha", "kisme"]
    return any(t in q for t in triggers)

def retrieve_chunks(query: str, top_k: int = 12, return_n: int = 6) -> pd.DataFrame:
    q_emb = create_embedding_batch([query])[0]
    emb_matrix = np.vstack(df["embedding"].values)

    sim = cosine_similarity(emb_matrix, [q_emb]).flatten()
    kw = build_keyword_score(df, query)

    # earlier-video preference
    early_boost = 1 / (df["number"].to_numpy() + 1.0)
    early_boost = (early_boost - early_boost.min()) / (early_boost.max() - early_boost.min() + 1e-9)

    w_sim = 1.0
    w_kw = 0.35
    w_early = 0.30 if wants_earliest(query) else 0.10

    final_score = (w_sim * sim) + (w_kw * kw) + (w_early * early_boost)

    idx = final_score.argsort()[::-1][:top_k]
    out = df.iloc[idx].copy()
    out["score"] = final_score[idx]

    # If user asks "where taught", pick earliest videos first among good matches
    if wants_earliest(query):
        out = out.sort_values(["number", "start"], ascending=True)

    return out.head(return_n)[["title", "number", "start", "end", "text"]]

# ----------------- LLM Answer (GPT-5, non-stream) -----------------
def answer_from_chunks(query: str, chunks: pd.DataFrame) -> str:
    chunks_json = chunks.to_json(orient="records")

    prompt = f"""
You are a strict course assistant.

You MUST answer ONLY using the provided JSON chunks.
Do NOT invent video numbers, timestamps, titles, or any facts not present in the chunks.

Provided chunks (JSON):
{chunks_json}

User question:
"{query}"

RULES:
1) Mention ONLY video numbers and timestamps that exist in the JSON chunks.
2) If the answer is not clearly present in the chunks, say:
   "I couldn't find this in the provided chunks. Please ask a question related to the course topics in the videos."
3) Keep it human and short.
4) End with: "Is there anything else I can help you with?"

Output format:
- Video <number>: <mm:ss>-<mm:ss> — <what is covered>
- (repeat if needed)
"""

    resp = client.responses.create(
        model="gpt-5",
        input=prompt,
    )
    return resp.output_text

# ----------------- Run -----------------
if __name__ == "__main__":
    incoming_query = input("Ask a Question: ").strip()
    if not incoming_query:
        print("Please type a question.")
        raise SystemExit

    chunks = retrieve_chunks(incoming_query)
    with open("prompt_context.json", "w", encoding="utf-8") as f:
        f.write(chunks.to_json(orient="records", indent=2))

    answer = answer_from_chunks(incoming_query, chunks)
    print(answer)

    with open("response.txt", "w", encoding="utf-8") as f:
        f.write(answer)
