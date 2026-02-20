from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from process_incoming import handle_query

app = FastAPI(title="RAG Teaching Assistant (Non-Streaming)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # production me apne frontend domain se restrict kar dena
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/ask_json")
def ask_json(req: AskRequest):
    answer = handle_query(req.question)
    return JSONResponse({"answer": answer})
