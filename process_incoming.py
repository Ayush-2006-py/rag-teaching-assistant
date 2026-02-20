import pandas as pd 
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import joblib
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

df = joblib.load("embeddings.joblib")

def create_embedding_batch(text_list):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text_list
    )
    return [item.embedding for item in response.data]

def inference_openai(prompt):
    response = client.responses.create(
        model="gpt-5",
        input=prompt
    )
    return response.output_text


def handle_query(incoming_query):

    question_embedding = create_embedding_batch([incoming_query])[0]

    similarities = cosine_similarity(
        np.vstack(df['embedding']), 
        [question_embedding]
    ).flatten()

    top_results = 3
    max_indx = similarities.argsort()[::-1][0:top_results]
    new_df = df.loc[max_indx]

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

    response = inference_openai(prompt)

    return response


