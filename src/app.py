from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
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
    return FileResponse("frontend/index.html")

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

@app.get("/financial-news")
async def get_financial_news():
    """
    Endpoint to serve financial news data for the news section.
    In a production environment, this would fetch from a real financial news API.
    """
    try:
        # Sample financial news data with realistic recent timestamps
        current_time = datetime.now()
        
        financial_news = [
            {
                "id": 1,
                "headline": "Federal Reserve Signals Potential Interest Rate Adjustments for 2024",
                "summary": "The Federal Reserve indicated possible changes to interest rates in the coming year, citing inflation concerns and economic growth targets. Market analysts are closely monitoring these developments for potential impacts on investment strategies.",
                "category": "markets",
                "source": "Financial Times",
                "date": (current_time - timedelta(hours=2)).strftime("%Y-%m-%d"),
                "time": (current_time - timedelta(hours=2)).strftime("%H:%M"),
                "icon": "fas fa-university",
                "url": "#"
            },
            {
                "id": 2,
                "headline": "Tech Giants Report Strong Q4 Earnings Despite Market Volatility",
                "summary": "Major technology companies exceeded expectations in their quarterly reports, showing resilience in a challenging market environment. Cloud services and AI investments continue to drive growth across the sector.",
                "category": "tech",
                "source": "TechCrunch",
                "date": (current_time - timedelta(hours=4)).strftime("%Y-%m-%d"),
                "time": (current_time - timedelta(hours=4)).strftime("%H:%M"),
                "icon": "fas fa-microchip",
                "url": "#"
            },
            {
                "id": 3,
                "headline": "Bitcoin Surges Above $50K as Institutional Adoption Increases",
                "summary": "Cryptocurrency markets experienced significant gains as more institutional investors enter the space. Bitcoin led the rally with increased trading volumes and renewed positive sentiment from major financial institutions.",
                "category": "crypto",
                "source": "CoinDesk",
                "date": (current_time - timedelta(hours=6)).strftime("%Y-%m-%d"),
                "time": (current_time - timedelta(hours=6)).strftime("%H:%M"),
                "icon": "fab fa-bitcoin",
                "url": "#"
            },
            {
                "id": 4,
                "headline": "Major Banks Announce Increased Investment in Digital Infrastructure",
                "summary": "Leading financial institutions are accelerating their digital transformation initiatives, investing billions in new technologies to improve customer experience and operational efficiency in response to changing consumer demands.",
                "category": "banking",
                "source": "Bloomberg",
                "date": (current_time - timedelta(hours=8)).strftime("%Y-%m-%d"),
                "time": (current_time - timedelta(hours=8)).strftime("%H:%M"),
                "icon": "fas fa-building",
                "url": "#"
            },
            {
                "id": 5,
                "headline": "Global Markets Show Mixed Results Amid Geopolitical Tensions",
                "summary": "International stock markets displayed varied performance as investors navigate ongoing geopolitical uncertainties and economic policy changes across major economies. Risk assessment strategies are being reassessed globally.",
                "category": "markets",
                "source": "Reuters",
                "date": (current_time - timedelta(hours=12)).strftime("%Y-%m-%d"),
                "time": (current_time - timedelta(hours=12)).strftime("%H:%M"),
                "icon": "fas fa-globe-americas",
                "url": "#"
            },
            {
                "id": 6,
                "headline": "Fintech Startups Secure Record Funding in Latest Investment Round",
                "summary": "Emerging financial technology companies raised unprecedented amounts in venture capital funding, signaling continued confidence in digital financial services innovation and the future of financial technology solutions.",
                "category": "tech",
                "source": "VentureBeat",
                "date": (current_time - timedelta(hours=14)).strftime("%Y-%m-%d"),
                "time": (current_time - timedelta(hours=14)).strftime("%H:%M"),
                "icon": "fas fa-rocket",
                "url": "#"
            },
            {
                "id": 7,
                "headline": "Central Bank Digital Currencies Gain Momentum Worldwide",
                "summary": "Several major economies announce progress in their central bank digital currency (CBDC) initiatives, potentially reshaping the future of monetary systems and digital payments infrastructure.",
                "category": "banking",
                "source": "Financial News",
                "date": (current_time - timedelta(hours=16)).strftime("%Y-%m-%d"),
                "time": (current_time - timedelta(hours=16)).strftime("%H:%M"),
                "icon": "fas fa-coins",
                "url": "#"
            },
            {
                "id": 8,
                "headline": "Ethereum Network Upgrade Shows Promising Results for Scalability",
                "summary": "The latest Ethereum network improvements demonstrate significant enhancements in transaction processing speed and reduced gas fees, potentially boosting adoption of decentralized finance applications.",
                "category": "crypto",
                "source": "CryptoNews",
                "date": (current_time - timedelta(hours=18)).strftime("%Y-%m-%d"),
                "time": (current_time - timedelta(hours=18)).strftime("%H:%M"),
                "icon": "fab fa-ethereum",
                "url": "#"
            }
        ]
        
        return {
            "articles": financial_news,
            "last_updated": current_time.isoformat(),
            "total_count": len(financial_news)
        }
        
    except Exception as e:
        print(f"Error in financial_news endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
