from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from typing import List, Dict, Any, Optional
from src.retrieval import search
from src.rbac import filter_hits_by_role
from src.llm_client import generate_answer

load_dotenv()

app = FastAPI(title="Intrabot-AI - Retrieval + Answer API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

class QueryIn(BaseModel):
    query: str
    top_k: int = 5
    role: str = "employee"
    use_llm: bool = True

@app.get("/")
def home():
    return {"status": "ok", "msg": "Intrabot-AI retrieval API. Use POST /query or POST /answer"}

@app.get("/actions/leave_request")
def get_leave_request():
    return {"steps": ["1. Log in to the HR portal at hr.company.com", "2. Navigate to 'Leave' section", "3. Click 'New Request'", "4. Fill in the required details (dates, type of leave)", "5. Submit the request", "6. Wait for approval from your manager"]}

@app.post("/query")
async def do_query(payload: QueryIn):
    try:
        # Perform the search
        res = search(payload.query, top_k=payload.top_k)
        
        # Process the search results
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        dists = res.get("distances", [[]])[0]
        
        hits = []
        for i, doc in enumerate(docs):
            meta = metas[i] if i < len(metas) else {}
            dist = dists[i] if i < len(dists) else None
            hits.append({
                "source": meta.get("source", ""), 
                "text": doc, 
                "distance": float(dist) if dist is not None else None, 
                "roles": meta.get("roles", "")
            })
        
        # Apply RBAC filtering
        filtered_hits = filter_hits_by_role(hits, payload.role)
        
        # Generate smart AI answer (works with or without filtered hits)
        answer = None
        if payload.use_llm:
            answer_result = generate_answer(payload.query, filtered_hits)
            answer = answer_result.get("answer")
        
        return {
            "query": payload.query, 
            "role": payload.role, 
            "hits": filtered_hits,
            "answer": answer
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/answer")
async def smart_answer(payload: QueryIn):
    """
    Enhanced endpoint for getting intelligent AI-generated answers.
    Uses the new smart response system that provides helpful answers even without context.
    """
    try:
        # First, get relevant documents
        res = search(payload.query, top_k=payload.top_k)
        
        # Process the search results
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        dists = res.get("distances", [[]])[0]
        
        hits = []
        for i, doc in enumerate(docs):
            meta = metas[i] if i < len(metas) else {}
            dist = dists[i] if i < len(dists) else None
            hits.append({
                "source": meta.get("source", ""),
                "text": doc,
                "distance": float(dist) if dist is not None else None,
                "roles": meta.get("roles", "")
            })
        
        # Apply RBAC filtering
        filtered_hits = filter_hits_by_role(hits, payload.role)
        
        # Generate smart AI response (works with or without retrieved documents)
        if payload.use_llm:
            result = generate_answer(payload.query, filtered_hits)
            return {
                "query": payload.query,
                "role": payload.role,
                "answer": result.get("answer", "I apologize, but I couldn't generate a response."),
                "sources": result.get("sources", []),
                "source": result.get("source", "ai_assistant"),
                "hits": filtered_hits
            }
        else:
            return {
                "query": payload.query,
                "role": payload.role,
                "hits": filtered_hits
            }
            
    except Exception as e:
        print(f"Error in smart_answer endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
