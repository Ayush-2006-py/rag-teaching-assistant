from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from process_incoming import handle_query_stream

app = FastAPI()

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- REQUEST MODEL (422 FIX) ----------
class AskRequest(BaseModel):
    question: str


# ---------- ROUTES ----------
@app.get("/")
def root():
    return {"status": "server running"}


@app.post("/ask_json")
def ask_json(req: AskRequest):

    generator = handle_query_stream(req.question)

    return StreamingResponse(
        generator,
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )

