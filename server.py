from fastapi import FastAPI
from pydantic import BaseModel
from process_incoming import handle_query

app = FastAPI()

class Question(BaseModel):
    question: str

@app.post("/ask")
def ask_question(q: Question):
    answer = handle_query(q.question)
    return {"answer": answer}
