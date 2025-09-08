# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Intrabot-AI is a Retrieval-Augmented Generation (RAG) chatbot system designed for organizational knowledge management. It combines vector search with AI-powered response generation to answer employee queries based on internal documentation while implementing role-based access control (RBAC).

## Architecture

### Core Components

- **Vector Search Engine**: ChromaDB with sentence-transformers embeddings for semantic document retrieval
- **AI Response Generation**: Google Gemini Pro API for generating context-aware answers
- **Role-Based Access Control**: Filters document access based on user roles (employee, hr, it, manager)
- **FastAPI Backend**: RESTful API with multiple endpoints for different query types
- **Frontend**: Simple HTML/JavaScript chat interface

### Dual Code Structure

The project has two parallel implementations:
- **Root level**: `api.py`, `gemini_client.py`, `retrieval.py`, `rbac.py` (original implementation)
- **src/ directory**: `src/app.py`, `src/llm_client.py`, `src/retrieval.py`, `src/rbac.py` (enhanced implementation)

The `src/` version includes fallback models (llama-cpp, GPT4All) and more sophisticated response generation.

### Data Flow

1. Documents in `offline-org-chatbot/data/` are ingested and chunked
2. Text chunks are embedded using sentence-transformers and stored in ChromaDB
3. User queries are embedded and matched against stored vectors
4. Retrieved documents are filtered by RBAC rules
5. Context is sent to Gemini Pro for answer generation

## Development Commands

### Setup and Installation
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env  # Create .env with GEMINI_API_KEY
```

### Data Ingestion
```bash
# Ingest documents from offline-org-chatbot/data/ into ChromaDB
python src/ingest.py

# Test retrieval without running the API server
python retrieval.py  # Root version
python -m src.retrieval  # Src version
```

### Running the Application

#### Using root-level implementation:
```bash
uvicorn api:app --reload --port 8000
```

#### Using src/ implementation:
```bash
uvicorn src.app:app --reload --port 8000
```

#### Frontend Access:
- Open browser to `http://localhost:8000/static/index.html`
- API documentation at `http://localhost:8000/docs`

### Testing Individual Components

#### Test vector search:
```bash
python retrieval.py  # Interactive query testing
```

#### Test LLM integration:
```bash
python -c "from gemini_client import generate_response; print(generate_response('Test query'))"
```

#### Test RBAC filtering:
```bash
python -c "from rbac import filter_hits_by_role; print(filter_hits_by_role([{'source': 'hr_faq.md', 'text': 'test'}], 'employee'))"
```

## Key Configuration

### Environment Variables
- `GEMINI_API_KEY`: Required for AI response generation
- `LLAMA_MODEL_PATH`: Optional path to local llama model (src version only)

### ChromaDB Configuration
- **Database Path**: `offline-org-chatbot/.chromadb`
- **Collection Name**: `intrabot_docs`
- **Embedding Model**: `all-MiniLM-L6-v2`

### Role Permissions (in `rbac.py`)
- **employee**: Access to `hr_faq.md`, `onboarding_guide.md`, `employee_handbook.md`
- **hr**: Access to `hr_faq.md`, `employee_handbook.md`
- **it**: Access to `onboarding_guide.md`
- **manager**: Full access to all documents

## API Endpoints

### Root Implementation (`api.py`)
- `POST /query`: Returns search results + AI-generated response
- `POST /chat`: Conversational interface with message history

### Src Implementation (`src/app.py`)
- `POST /query`: Returns search results with optional LLM response
- `POST /answer`: Direct AI answer endpoint for chat interfaces
- `GET /actions/leave_request`: Predefined action for leave request steps

## File Structure Patterns

### Data Files
- Store organizational documents in `offline-org-chatbot/data/` as `.md` or `.txt`
- Files are automatically assigned roles based on filename patterns (hr_, it_, policies_, etc.)

### Model Integration
- Primary: Gemini Pro via Google's GenerativeAI API
- Fallbacks: llama-cpp and GPT4All (src version only)
- Embedding: sentence-transformers with `all-MiniLM-L6-v2`

## Common Development Tasks

### Adding New Document Types
1. Add files to `offline-org-chatbot/data/`
2. Update role mappings in `get_roles()` function in `src/ingest.py`
3. Update RBAC rules in `rbac.py`
4. Run `python src/ingest.py` to re-index

### Modifying Role Permissions
- Edit `ROLE_RULES` dictionary in `rbac.py`
- No re-ingestion needed for permission changes

### Changing Embedding Models
- Update `MODEL_NAME` in both `retrieval.py` and `src/ingest.py`
- Re-run ingestion to rebuild embeddings

### Debugging Query Issues
1. Test retrieval: `python retrieval.py`
2. Check RBAC filtering manually
3. Test LLM integration separately
4. Review ChromaDB collection contents via API

## Dependencies and Versions

Key packages:
- `fastapi>=0.68.0`: Web framework
- `sentence-transformers>=2.2.2`: Text embeddings
- `chromadb>=0.3.21`: Vector database
- `google-generativeai>=0.3.0`: Gemini API client
- `uvicorn>=0.15.0`: ASGI server
