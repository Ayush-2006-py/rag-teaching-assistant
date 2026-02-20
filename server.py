from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from process_incoming import handle_query_stream

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask")
async def ask(data: dict):
    question = data["question"]

    generator = handle_query_stream(question)

    return StreamingResponse(generator, media_type="text/plain")
