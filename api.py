# fastapi.py - FastAPI wrapper for chat.py with separated endpoints
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
from chat import ask_perplexity_style

app = FastAPI(title="RAG Chat API", version="2.0")

# ======================
# Models
# ======================
class ChatRequest(BaseModel):
    query: str

class ChatAnswerResponse(BaseModel):
    query: str
    answer: str

class WebSourcesResponse(BaseModel):
    sources: Dict[str, Any]

class RelatedPromptsResponse(BaseModel):
    related_prompts: list

# ======================
# Global cache (simple in-memory for demo)
# ======================
_last_result: Dict[str, Any] = {}

# ======================
# Endpoints
# ======================

@app.post("/chat", response_model=ChatAnswerResponse)
async def chat_endpoint(req: ChatRequest):
    """
    Run the full RAG pipeline, return only the answer.
    Sources & related prompts are cached for other endpoints.
    """
    global _last_result
    _last_result = ask_perplexity_style(req.query)
    return {"query": _last_result["query"], "answer": _last_result["answer"]}

@app.get("/websource", response_model=WebSourcesResponse)
async def websource_endpoint():
    """
    Return categorized web + KB sources from the last chat query.
    """
    if not _last_result:
        return {"sources": {}}
    return {"sources": _last_result["sources"]}

@app.get("/related", response_model=RelatedPromptsResponse)
async def related_endpoint():
    """
    Return related prompts from the last chat query.
    """
    if not _last_result:
        return {"related_prompts": []}
    return {"related_prompts": _last_result["related_prompts"]}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "RAG Chat API"}
