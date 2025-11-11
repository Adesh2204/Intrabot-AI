# Intrabot-Ai/api.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from retrieval import search
from rbac import filter_hits_by_role
from gemini_client import generate_response
import os

app = FastAPI(title="Intrabot-AI - Retrieval API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

class QueryIn(BaseModel):
    query: str
    top_k: int = 4
    role: str = "employee"

@app.get("/")
def home():
    """Redirect to the frontend interface"""
    try:
        frontend_path = os.path.join("frontend", "index.html")
        if os.path.exists(frontend_path):
            return FileResponse(frontend_path)
        else:
            return {"status": "ok", "msg": "Intrabot-AI retrieval API. Frontend available at /static/index.html"}
    except Exception as e:
        return {"status": "ok", "msg": "Intrabot-AI retrieval API. Use POST /query"}

@app.get("/app")
def app_redirect():
    """Alternative route to access the frontend"""
    frontend_path = os.path.join("frontend", "index.html") 
    return FileResponse(frontend_path)

class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    role: str = "employee"

class AnswerRequest(BaseModel):
    query: str
    top_k: int = 4
    role: str = "employee"
    use_llm: bool = True

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

@app.post("/answer")
async def answer_endpoint(payload: AnswerRequest):
    """Legacy endpoint for frontend compatibility"""
    try:
        # Run vector search
        res = search(payload.query, top_k=payload.top_k)

        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        dists = res.get("distances", [[]])[0]

        hits = []
        sources = []
        for i, doc in enumerate(docs):
            meta = metas[i] if i < len(metas) else {}
            dist = dists[i] if i < len(dists) else None
            source = meta.get("source", "unknown")
            
            hits.append({
                "source": source,
                "text": doc,
                "distance": float(dist) if dist is not None else None
            })
            if source not in sources:
                sources.append(source)

        # Apply RBAC filter
        filtered_hits = filter_hits_by_role(hits, payload.role)
        
        # Extract context from search results
        context = "\n".join([hit["text"] for hit in filtered_hits])
        
        # Generate response using Gemini if requested
        if payload.use_llm and context:
            try:
                ai_response = generate_response(query=payload.query, context=context)
                # If response starts with "Error", fallback to basic response
                if ai_response.startswith("Error"):
                    ai_response = f"Based on the available information: {context[:200]}..."
            except Exception:
                ai_response = f"Based on the available information: {context[:200]}..."
        else:
            ai_response = f"Found {len(filtered_hits)} relevant document(s) for your query."
        
        return {
            "answer": ai_response,
            "sources": sources,
            "hits": filtered_hits,
            "source": "online" if payload.use_llm else "offline"
        }
        
    except Exception as e:
        return {
            "answer": "I'm sorry, I encountered an error while processing your request. Please try again.",
            "sources": [],
            "hits": [],
            "source": "error"
        }

@app.get("/actions/leave_request")
async def leave_request_steps():
    """Provide leave request steps"""
    return {
        "steps": [
            "Log into the HR portal using your employee credentials",
            "Navigate to the 'Leave Management' section",
            "Click on 'Submit New Leave Request'", 
            "Select the type of leave (Annual, Sick, Personal, etc.)",
            "Choose your leave start and end dates",
            "Enter a brief reason for your leave",
            "Upload any required supporting documents",
            "Submit the request for manager approval",
            "Check your email for approval notifications"
        ]
    }

@app.get("/financial-news")
async def get_financial_news():
    """Provide sample financial news"""
    return {
        "news": [
            {
                "title": "Market Update: Tech Stocks Rally",
                "summary": "Technology sector shows strong performance with AI companies leading gains",
                "category": "markets",
                "timestamp": "2 hours ago"
            },
            {
                "title": "Federal Reserve Policy Decision",
                "summary": "Central bank maintains current interest rate amid economic stability",
                "category": "policy", 
                "timestamp": "4 hours ago"
            },
            {
                "title": "Quarterly Earnings Preview",
                "summary": "Major corporations prepare to release Q4 earnings reports",
                "category": "earnings",
                "timestamp": "6 hours ago"
            }
        ]
    }

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