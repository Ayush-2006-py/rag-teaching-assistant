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

    # 3) Prompt (same as your original)
    prompt = f'''I am teaching web development in my Sigma web development course. Here are video subtitle chunks containing video title, video number, start time in seconds, end time in seconds, the text at that time:

{new_df[["title", "number", "start", "end", "text"]].to_json(orient="records")}
---------------------------------
"{incoming_query}"
User asked this question related to the video chunks, you have to answer in a human way 
(dont mention the above format, its just for you) where and how much content is taught in which video 
(in which video and at what timestamp) and guide the user to go to that particular video. 
If user asks unrelated question, tell him that you can only answer questions related to the course
also if the asked question is not in the chunks dont give any video number just guide the user what to ask related to course
and just give the video numbers per the questions asked. also at the end ask question is there anything that i can help you with
also dont give examples what to ask 

if the user ask for brief or summary of any topic just answer in breif 
as taught in course but
use this only when the user ask about brief of any topic in  the course 
'''

    # 4) NON-STREAM response using GPT-5
    resp = client.responses.create(
        model="gpt-5",
        input=prompt,
    )

    # Responses API returns output text in resp.output_text (recommended way)
    return resp.output_text




