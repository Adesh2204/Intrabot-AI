# Intrabot-Ai/src/llm_client.py
import os
import re
import google.generativeai as genai
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyAL2zfBeWYIUlivvRLFln5OSKkaNIVdPqE')

# Initialize Gemini
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        _gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        print("[llm_client] Successfully initialized Gemini Pro model")
    except Exception as e:
        print(f"[llm_client] Failed to initialize Gemini: {e}")
        _gemini_model = None
else:
    print("[llm_client] GEMINI_API_KEY not found in environment variables")
    _gemini_model = None

# Fallback models
_llm = None
MODEL_ENV = "LLAMA_MODEL_PATH"
DEFAULT_MODEL_PATH = "models/ggml-model.bin"

# Only initialize fallback models if Gemini is not available
if _gemini_model is None:
    try:
        from llama_cpp import Llama
        model_path = os.environ.get(MODEL_ENV, DEFAULT_MODEL_PATH)
        if os.path.exists(model_path):
            print(f"[llm_client] Loading Llama model from: {model_path}")
            _llm = Llama(model_path=model_path)
        else:
            print(f"[llm_client] llama_cpp available but model not found at: {model_path}")
    except Exception as e:
        print(f"[llm_client] llama_cpp not available or failed to load: {e}")

    # Try GPT4All as fallback
    if _llm is None:
        try:
            from gpt4all import GPT4All
            print("[llm_client] Loading GPT4All model")
            _llm = GPT4All("ggml-gpt4all-j-v1.3-groovy.bin")
        except Exception as e:
            print(f"[llm_client] GPT4All not available or failed to load: {e}")

GEMINI_PROMPT_TEMPLATE = """You are Intrabot-AI, an intelligent organizational assistant with expertise in business operations, finance, HR, IT, and general workplace assistance.

Context (from organizational knowledge base):
{context}

Question: {query}

Please provide a helpful, detailed, and professional response. If specific organizational context is provided above, prioritize that information. Otherwise, provide general best practices and guidance based on your knowledge.

Answer:"""

FALLBACK_PROMPT_TEMPLATE = """You are Intrabot-AI, an organizational assistant.
Answer questions based only on the given context and general organizational knowledge.

Context:
{context}

Question:
{query}

Answer:
"""

def _build_context(retrieved: List[Dict]) -> str:
    parts = []
    for r in retrieved:
        src = r.get("source", "unknown")
        txt = r.get("text", "").strip()
        parts.append(f"Source: {src}\n{txt}")
    return "\n\n---\n\n".join(parts)

def _first_sentences(text: str, max_sents=2) -> List[str]:
    # crude sentence splitter
    sents = re.split(r'(?<=[\.\?\!])\s+', text.strip())
    out = []
    for s in sents:
        s = s.strip()
        if s:
            out.append(s)
        if len(out) >= max_sents:
            break
    return out

def generate_smart_response(query: str, retrieved: List[Dict] = None) -> Dict:
    """
    Generate intelligent AI responses using Gemini, with or without context.
    """
    context = ""
    sources = []
    
    # Build context if retrieved documents are available
    if retrieved:
        context = _build_context(retrieved)
        sources = list(set(doc.get("source", "") for doc in retrieved if doc.get("source")))
    else:
        context = "No specific organizational context available."
    
    # Try Gemini first
    if _gemini_model:
        try:
            prompt = GEMINI_PROMPT_TEMPLATE.format(
                context=context,
                query=query
            )
            
            response = _gemini_model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": 512,
                    "temperature": 0.7,
                }
            )

            answer = response.text.strip()
            if answer:
                return {
                    "answer": answer,
                    "sources": sources,
                    "source": "gemini" if not sources else "mixed"
                }
                
        except Exception as e:
            print(f"[llm_client] Gemini error: {e}")
    
    # Fallback to predefined smart responses for common queries
    return _get_smart_fallback_response(query, retrieved)

def _get_smart_fallback_response(query: str, retrieved: List[Dict]) -> Dict:
    """Provide intelligent fallback responses for common business queries."""
    query_lower = query.lower()
    
    # ITR/Tax related queries
    if any(keyword in query_lower for keyword in ["itr", "tax", "income tax", "file tax", "tax return"]):
        return {
            "answer": """**How to File Income Tax Return (ITR):**

📋 **Documents Required:**
• PAN Card and Aadhaar Card
• Form 16 (from employer)
• Bank statements for the financial year
• Investment proofs (80C, 80D, etc.)
• Property documents (if applicable)
• Capital gains statements

💻 **Filing Process:**
1. Visit the official Income Tax e-filing portal: incometaxindiaefiling.gov.in
2. Register/Login with your credentials
3. Select appropriate ITR form:
   - **ITR-1**: Salaried individuals with income up to ₹50 lakhs
   - **ITR-2**: Individuals with capital gains or multiple house properties
   - **ITR-3**: Business/Professional income
4. Fill in all required details carefully
5. Verify income, deductions, and tax calculations
6. Upload supporting documents
7. Submit and e-verify using Aadhaar OTP/Net Banking

⏰ **Important Deadlines:**
• Original due date: July 31st
• Extended due date: Usually December 31st (check current year)

💡 **Pro Tips:**
• Keep digital copies of all documents
• Double-check calculations before submission
• Consider professional help for complex returns

Would you like specific guidance on any particular aspect of ITR filing?""",
            "sources": [],
            "source": "ai_assistant"
        }
    
    # Bank statement queries
    elif any(keyword in query_lower for keyword in ["bank statement", "bank data", "financial statement", "account statement"]):
        return {
            "answer": """**Bank Statement Analysis & Requirements:**

📊 **For ITR Filing, I'll need the following bank data:**

**Essential Information:**
• Account holder name and account numbers
• Opening and closing balances for the financial year
• Interest earned on savings/FD accounts
• TDS deducted by banks
• Loan EMI payments (for tax deductions)
• Major transactions above ₹2 lakhs

**Government-Issued Bank Statements:**
• Download statements directly from net banking
• Visit branch for certified/stamped statements
• Ensure statements cover the complete financial year (April 1 - March 31)

**For Loan/Financial Applications:**
• Last 6-12 months' statements
• Salary credit entries highlighted
• Consistent balance maintenance proof
• No suspicious or irregular transactions

**Digital Formats:**
• PDF statements with bank seal
• Excel format for easy data extraction
• Ensure all pages are included

📋 **What specific bank data do you need help with?**
• Tax calculation assistance?
• Loan application support?
• Investment tracking?
• Business financial analysis?

Please share your specific requirement, and I'll provide detailed guidance!""",
            "sources": [],
            "source": "ai_assistant"
        }
    
    # Leave application queries
    elif any(keyword in query_lower for keyword in ["leave", "apply leave", "sick leave", "vacation"]):
        return {
            "answer": """**Leave Application Process:**

📝 **Standard Leave Application Format:**

Subject: Application for [Type of Leave]

Dear [Manager's Name/HR],

I would like to request [sick/casual/vacation] leave from [start date] to [end date] due to [reason].

**Leave Details:**
• Duration: [X] days
• Reason: [Brief explanation]
• Contact: [Phone number for emergencies]
• Work handover: [Mention colleague handling responsibilities]

I will ensure all pending tasks are completed/delegated before my leave.

Thank you for your consideration.

Best regards,
[Your name]

**📋 Process Steps:**
1. Check leave balance in HR portal
2. Plan work handover
3. Submit application with adequate notice
4. Await manager approval
5. Update team calendar

**💡 Best Practices:**
• Apply at least 3-5 days in advance
• Provide emergency contact
• Set up email auto-reply
• Brief team on urgent matters

Need help with a specific type of leave application?""",
            "sources": [],
            "source": "ai_assistant"
        }
    
    # General business/financial queries
    elif any(keyword in query_lower for keyword in ["calculate", "financial", "business", "accounting", "tally"]):
        return {
            "answer": """**Financial Calculation & Business Assistance:**

🧮 **I can help you with:**

**Tax Calculations:**
• Income tax liability calculation
• TDS computation
• Advance tax planning
• Capital gains calculation

**Business Financials:**
• Profit & Loss analysis
• GST calculations
• Cash flow projections
• ROI analysis

**Personal Finance:**
• EMI calculations
• Investment planning
• Retirement planning
• Insurance needs assessment

**Accounting Support:**
• Tally data reconciliation
• Balance sheet preparation
• Expense categorization
• Compliance checklists

📊 **To provide accurate calculations, please share:**
• Specific calculation type needed
• Relevant financial figures
• Time period (financial year, month, etc.)
• Purpose of calculation

**Example:** "Calculate income tax for salary of ₹8,00,000 with 80C investments of ₹1,50,000"

What specific calculation or analysis do you need help with?""",
            "sources": [],
            "source": "ai_assistant"
        }
    
    # Default intelligent response
    else:
        if retrieved:
            # If we have context but no specific handler, try to use retrieved info
            top = retrieved[:2]
            info_pieces = []
            for doc in top:
                text = doc.get("text", "").strip()[:200]
                if text:
                    info_pieces.append(text)
            
            if info_pieces:
                return {
                    "answer": f"Based on the available information:\n\n{' '.join(info_pieces)}\n\nIs there something specific you'd like to know more about?",
                    "sources": list(set(doc.get("source", "") for doc in retrieved if doc.get("source"))),
                    "source": "knowledge_base"
                }
        
        return {
            "answer": """I'm Intrabot-AI, your intelligent organizational assistant! 🤖

I can help you with:
• **Tax & Finance**: ITR filing, tax calculations, bank statements
• **HR Matters**: Leave applications, policies, procedures
• **Business Operations**: Accounting, compliance, documentation
• **General Assistance**: Process guidance, best practices

What would you like assistance with today? Please feel free to ask specific questions!""",
            "sources": [],
            "source": "ai_assistant"
        }

def generate_answer(query: str, retrieved: List[Dict], max_tokens: int = 512) -> Dict:
    """
    Generate intelligent AI-powered answers using the new smart response system.

    Args:
        query: The user's question
        retrieved: List of retrieved documents with source and text
        max_tokens: Maximum tokens for the response (increased for better responses)

    Returns:
        Dict containing 'answer', 'sources', and 'source'
    """
    # Use the new smart response system that handles both context and no-context scenarios
    result = generate_smart_response(query, retrieved)
    
    # Ensure backward compatibility with existing API expectations
    return {
        "answer": result.get("answer", "I apologize, but I couldn't generate a response at the moment."),
        "sources": result.get("sources", []),
        "source": result.get("source", "ai_assistant")
    }
