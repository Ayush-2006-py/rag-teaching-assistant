from fastapi import FastAPI
from pydantic import BaseModel
from process_incoming import handle_query
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class Question(BaseModel):
    question: str

@app.post("/ask")
def ask_question(q: Question):
    answer = handle_query(q.question)
    return {"answer": answer}
