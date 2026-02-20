import os
import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# embeddings.joblib must exist alongside this file (or correct path)
df = joblib.load("embeddings.joblib")


def create_embedding_batch(text_list):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text_list
    )
    return [item.embedding for item in response.data]


def handle_query(incoming_query: str) -> str:
    incoming_query = (incoming_query or "").strip()
    if not incoming_query:
        return "⚠️ Please type a question."

    # 1) Embed the question
    question_embedding = create_embedding_batch([incoming_query])[0]

    # 2) Similarities
    emb_matrix = np.vstack(df["embedding"].values)
    similarities = cosine_similarity(emb_matrix, [question_embedding]).flatten()

    top_results = 3
    max_indx = similarities.argsort()[::-1][:top_results]
    new_df = df.iloc[max_indx]

    prompt = f'''
You are a strict course assistant. 
You MUST answer ONLY using the provided video chunks.

Here are the relevant subtitle chunks:
{new_df[["title", "number", "start", "end", "text"]].to_json(orient="records")}

User question:
"{incoming_query}"

---------------- RULES ----------------
1. Only use the video numbers and timestamps from the chunks above.
2. NEVER invent any video number or timestamp.
3. If the topic is not clearly found in these chunks, say:
   "I could not find this topic in the provided video chunks. Please ask about topics covered in the course."
4. Mention only the videos that actually contain the topic.
5. Be direct and helpful.
6. At the end ask: "Is there anything else I can help you with?"

FORMAT:
- Video X (timestamp)
- Short explanation
'''



    # 4) NON-STREAM response using GPT-5
    resp = client.responses.create(
        model="gpt-5",
        input=prompt,
    )

    # Responses API returns output text in resp.output_text (recommended way)
    return resp.output_text
