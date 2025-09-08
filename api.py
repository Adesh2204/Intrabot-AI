# Intrabot-Ai/api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from retrieval import search
from rbac import filter_hits_by_role
from gemini_client import generate_response

app = FastAPI(title="Intrabot-AI - Retrieval API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

class QueryIn(BaseModel):
    query: str
    top_k: int = 4
    role: str = "employee"

@app.get("/")
def home():
    return {"status": "ok", "msg": "Intrabot-AI retrieval API. Use POST /query"}

class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    role: str = "employee"

@app.post("/query")
async def do_query(payload: QueryIn):
    try:
        # Run vector search
        res = search(payload.query, top_k=payload.top_k)

        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        dists = res.get("distances", [[]])[0]

        hits = []
        for i, doc in enumerate(docs):
            meta = metas[i] if i < len(metas) else {}
            dist = dists[i] if i < len(dists) else None
            hits.append({
                "source": meta.get("source"),
                "text": doc,
                "distance": float(dist) if dist is not None else None
            })

        # Apply RBAC filter
        filtered_hits = filter_hits_by_role(hits, payload.role)
        
        # Extract context from search results
        context = "\n".join([hit["text"] for hit in filtered_hits])
        
        # Generate response using Gemini
        ai_response = generate_response(query=payload.query, context=context)
        
        return {
            "query": payload.query,
            "role": payload.role,
            "hits": filtered_hits,
            "response": ai_response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_endpoint(chat_request: ChatRequest):
    try:
        # Format conversation history for the model
        conversation = "\n".join(
            [f"{msg.role}: {msg.content}" for msg in chat_request.messages]
        )
        
        # Get the latest user message
        user_message = next(
            (msg.content for msg in reversed(chat_request.messages) if msg.role == "user"),
            ""
        )
        
        if not user_message:
            raise HTTPException(status_code=400, detail="No user message found in chat history")
        
        # Generate response using Gemini with conversation history as context
        ai_response = generate_response(
            query=user_message,
            context=f"Conversation history:\n{conversation}"
        )
        
        return {
            "role": "assistant",
            "content": ai_response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))